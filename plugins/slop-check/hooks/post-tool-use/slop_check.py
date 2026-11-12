"""書き込むツールの中身を AI slop の単語の対応表で照合し、ヒットした単語の通知を返す PostToolUse のフック。

標準入力の PostToolUse の入力から書き込んだ中身を取り出し、ヒットした行があれば NG と OK の表を持つ通知の文を
`hookSpecificOutput.additionalContext` で標準出力へ出す。書き込みは止めず、終了コードは常に 0。
Python の標準ライブラリだけで書き、端末の python3（3.12 以上）で起動する。

Usage:
# PostToolUse の入力を標準入力で渡す
echo '{"tool_name": "Write", "tool_input": {"content": "本文"}}' | python3 slop_check.py
"""

import argparse
import io
import json
import os
import re
import sys
import traceback
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

# 対応表のコピーのファイル名（このファイルと同じフォルダに置く）
WORD_LIST_FILE = "word-list-ai-slop.json"

# 組み込みの書き込むツール → 中身を持つ tool_input のキー（Edit はファイル全体を読めないときだけ使う）
BUILTIN_TOOLS: dict[str, str] = {
    "Write": "content",
    "Edit": "new_string",
    "NotebookEdit": "new_source",
}

# MCP サーバーを見分ける単語 → 対象のツール名の集合
MCP_TOOLS: dict[str, frozenset[str]] = {
    "project-index": frozenset({"write_docs"}),
    "ai-monitor": frozenset(
        {
            "comment",
            "reply_comment",
            "reply_review_thread",
            "create_review_comment",
            "create_file_comment",
            "create_issue",
            "create_draft_pr",
            "update_body",
            "update_title",
            "add_notice_row",
            "notify",
            "create_defect_issue",
            "create_monitor_rule_issue",
            "create_plugin_rule_issue",
        }
    ),
    "mindstella": frozenset(
        {"add", "batch", "update", "reply", "new_thread", "edit_option", "update_thread"}
    ),
}

# 照合しない MCP の引数のキー（識別子を持つキー）。これに加えて _id で終わるキーも除く
EXCLUDED_KEYS = frozenset(
    {
        "id",
        "ids",
        "path",
        "paths",
        "file_path",
        "url",
        "source",
        "kind",
        "op",
        "cwd",
        "worktree",
        "branch",
        "sender",
        "receiver",
        "labels",
    }
)

# 照合しない書き込む先（対応表の正本とコピー）
WORD_LIST_PATH = re.compile(
    r"(?:^|/)docs/word-list/[^/]+\.ya?ml$|(?:^|/)hooks/post-tool-use/word-list-[^/]+\.json$"
)

# 通知の文の前半（表の前の 2 行と表の見出し）
NOTICE_HEAD = (
    "AI がよく使う単語（AI slop）が入っています。OK の単語に置き換えてください。\n"
    "NG の単語でないと意味が通らない理由があるときだけ、そのままにしてかまいません。\n"
    "\n"
    "| NG | OK |\n"
    "| --- | --- |"
)

# 通知の文の後半（規約を search_docs で参照する案内）
NOTICE_TAIL = (
    "\n"
    "まだ読んでいなければ、用途に合う規約を読んでください。\n"
    "- 文書・コメント: 規約『文章の書き方』\n"
    '  mcp__plugin_project-index_project-index__search_docs（source: "knowledge", filter: {"field": "id", "op": "eq", "values": ["convention-writing-style"]}, view: "full"）\n'
    "- 画面の文言: 規約『入力と文言』\n"
    '  mcp__plugin_project-index_project-index__search_docs（source: "knowledge", filter: {"field": "id", "op": "eq", "values": ["ui-input-wording"]}, view: "full"）'
)

# MCP ツールの名前の接頭辞と、サーバーの部分とツール名の区切り
_MCP_PREFIX = "mcp__"
_MCP_SEPARATOR = "__"

# project-index の書き込むツールの名前
_WRITE_DOCS = "write_docs"

# 対応表の文書の ID の接頭辞と種類
_WORD_LIST_ID_PREFIX = "word-list-"
_WORD_LIST_KIND = "word-list"


@dataclass(frozen=True)
class Entry:
    """対応表のコピーの 1 行を、照合に使う構造にしたもの。"""

    id: str
    ng: str
    # 置き換え先の単語（1 件以上）
    ok: tuple[str, ...]
    # pattern をコンパイルしたもの。pattern が無い行は ng をエスケープしてコンパイルしたもの
    matcher: re.Pattern[str]
    # ヒットの開始位置を含むなら除く文字列
    allow: tuple[str, ...]
    # OK の後ろに括弧で添える補足
    note: str | None


def _use_utf8(stream: object) -> None:
    """標準入出力を UTF-8 にする（Windows の既定のエンコーディングで読み書きしない）。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8")


def _default_word_list() -> Path:
    """対応表のコピーの既定のパスを返す。"""
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root) / "hooks" / "post-tool-use" / WORD_LIST_FILE
    return Path(__file__).with_name(WORD_LIST_FILE)


def main(argv: Sequence[str] | None = None, *, word_list: Path | None = None) -> int:
    """標準入力の PostToolUse の入力を照合し、ヒットがあれば通知の JSON を標準出力へ出す。"""
    parser = argparse.ArgumentParser(
        description="書き込んだ中身を AI slop の単語の対応表で照合する"
    )
    parser.parse_args(argv)
    _use_utf8(sys.stdin)
    _use_utf8(sys.stdout)
    _use_utf8(sys.stderr)

    try:
        # 入力が読めないときは、書き込みの結果を変えずに終わる
        try:
            payload: object = json.loads(sys.stdin.read())
        except ValueError as error:
            print(f"PostToolUse の入力を JSON として読めません: {error}", file=sys.stderr)
            return 0
        tool_name, tool_input = _tool_of(payload)
        if tool_name is None or tool_input is None:
            print(
                "PostToolUse の入力を JSON として読めません: tool_name・tool_input がありません",
                file=sys.stderr,
            )
            return 0

        # 対象外のツールと対応表への書き込みは、対応表を読む前に終わる
        if not is_target(tool_name) or is_word_list_write(tool_name, tool_input):
            return 0
        text = extract_text(tool_name, tool_input)
        if not text:
            return 0

        path = word_list if word_list is not None else _default_word_list()
        try:
            entries = load_entries(path)
        except (OSError, ValueError) as error:
            print(f"対応表を読めません: {path}: {error}", file=sys.stderr)
            return 0

        hits = find_hits(text, entries)
        if hits:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": build_notice(hits),
                }
            }
            print(json.dumps(output, ensure_ascii=False))
    except Exception:  # noqa: BLE001 - 想定していない例外も書き込みの結果を変えずに traceback だけ出す
        traceback.print_exc()
    return 0


def _tool_of(payload: object) -> tuple[str | None, Mapping[str, object] | None]:
    """PostToolUse の入力から tool_name と tool_input を取り出す。無ければ None。"""
    if not isinstance(payload, dict):
        return None, None
    data = cast("dict[str, object]", payload)
    tool_name = data.get("tool_name")
    tool_input = data.get("tool_input")
    return (
        tool_name if isinstance(tool_name, str) else None,
        cast("dict[str, object]", tool_input) if isinstance(tool_input, dict) else None,
    )


def _split_mcp(tool_name: str) -> tuple[str, str] | None:
    """MCP ツールの名前を、サーバーの部分とツール名に分ける。MCP ツールでなければ None。"""
    if not tool_name.startswith(_MCP_PREFIX):
        return None
    server, separator, name = tool_name[len(_MCP_PREFIX) :].rpartition(_MCP_SEPARATOR)
    if not separator:
        return None
    return server, name


def is_target(tool_name: str) -> bool:
    """ツール名が組み込みの書き込むツールか、対象の MCP ツールかを返す。"""
    if tool_name in BUILTIN_TOOLS:
        return True
    parts = _split_mcp(tool_name)
    if parts is None:
        return False
    server, name = parts
    # サーバーの部分に見分ける単語を含み、そのサーバーの対象のツールであるか
    return any(word in server and name in names for word, names in MCP_TOOLS.items())


def is_word_list_write(tool_name: str, tool_input: Mapping[str, object]) -> bool:
    """書き込む先が対応表の正本かコピーかを返す。"""
    # 組み込みのツール: 書き込む先のパスで判定する
    if tool_name in BUILTIN_TOOLS:
        key = "notebook_path" if tool_name == "NotebookEdit" else "file_path"
        path = tool_input.get(key)
        return isinstance(path, str) and WORD_LIST_PATH.search(path.replace("\\", "/")) is not None
    # write_docs: 全ての操作が対応表の文書に向いているときだけ
    parts = _split_mcp(tool_name)
    if parts is None or parts[1] != _WRITE_DOCS:
        return False
    operations = tool_input.get("operations")
    if not isinstance(operations, list) or not operations:
        return False
    return all(_is_word_list_operation(operation) for operation in cast("list[object]", operations))


def _is_word_list_operation(operation: object) -> bool:
    """write_docs の操作 1 件が対応表の文書を書き込むかを返す。"""
    if not isinstance(operation, dict):
        return False
    data = cast("dict[str, object]", operation)
    doc_id = data.get("id")
    return (isinstance(doc_id, str) and doc_id.startswith(_WORD_LIST_ID_PREFIX)) or data.get(
        "kind"
    ) == _WORD_LIST_KIND


def extract_text(tool_name: str, tool_input: Mapping[str, object]) -> str:
    """ツールごとに、照合する中身を取り出す。取り出せなければ空文字列。"""
    # Edit: 修正後のファイル全体。読めなければ置き換え後の文字列
    if tool_name == "Edit":
        path = tool_input.get("file_path")
        if isinstance(path, str):
            try:
                return Path(path).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                pass
    # 組み込みのツール: 中身を持つキーの値
    if tool_name in BUILTIN_TOOLS:
        value = tool_input.get(BUILTIN_TOOLS[tool_name])
        return value if isinstance(value, str) else ""
    # MCP ツール: 識別子のキーを除いた全ての文字列の値
    return "\n".join(collect_strings(tool_input))


def collect_strings(value: object) -> list[str]:
    """辞書・配列をたどり、除くキーの下を飛ばして文字列の値を出現の順に集める。"""
    if isinstance(value, str):
        return [value]
    strings: list[str] = []
    if isinstance(value, dict):
        for key, child in cast("dict[object, object]", value).items():
            # 識別子を持つキーは照合しない
            if isinstance(key, str) and (key in EXCLUDED_KEYS or key.endswith("_id")):
                continue
            strings.extend(collect_strings(child))
    elif isinstance(value, list):
        for child in cast("list[object]", value):
            strings.extend(collect_strings(child))
    return strings


def _strings(value: object) -> tuple[str, ...]:
    """文字列の配列を tuple にする。配列でなければ空。"""
    if not isinstance(value, list):
        return ()
    return tuple(item for item in cast("list[object]", value) if isinstance(item, str))


def compile_entry(row: Mapping[str, object]) -> Entry:
    """対応表の 1 行の辞書から、照合に使う行を作る。pattern が読めなければ re.error を送出する。"""
    ng = str(row["ng"])
    pattern = row.get("pattern")
    note = row.get("note")
    return Entry(
        id=str(row["id"]),
        ng=ng,
        ok=_strings(row.get("ok")),
        matcher=re.compile(pattern if isinstance(pattern, str) else re.escape(ng)),
        allow=_strings(row.get("allow")),
        note=note if isinstance(note, str) else None,
    )


def load_entries(path: Path) -> list[Entry]:
    """対応表のコピーを読み、行の並びを返す。正規表現として読めない行は除く。"""
    data: object = json.loads(path.read_text(encoding="utf-8"))
    rows = cast("dict[str, object]", data).get("entries") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        message = "entries が配列ではありません"
        raise ValueError(message)
    entries: list[Entry] = []
    for row in cast("list[object]", rows):
        if not isinstance(row, dict):
            continue
        mapping = cast("dict[str, object]", row)
        try:
            entries.append(compile_entry(mapping))
        except re.error as error:
            # 読めない行だけを飛ばし、残りの行で照合を続ける
            print(
                f"対応表の行 {mapping.get('id')} の pattern を読めません: {error}", file=sys.stderr
            )
    return entries


def entry_hits(text: str, entry: Entry) -> bool:
    """文字列に、allow に当たらないヒットが 1 つ以上あるかを返す。"""
    # allow の各文字列の出現の範囲
    allowed = [
        (found.start(), found.end())
        for word in entry.allow
        for found in re.finditer(re.escape(word), text)
    ]
    for hit in entry.matcher.finditer(text):
        # ヒットの開始位置を含む allow の出現が無ければ、そのヒットを残す
        if not any(start <= hit.start() < end for start, end in allowed):
            return True
    return False


def find_hits(text: str, entries: Sequence[Entry]) -> list[Entry]:
    """対応表の行のうち、中身にヒットした行を対応表の並びで返す。"""
    return [entry for entry in entries if entry_hits(text, entry)]


def build_notice(hits: Sequence[Entry]) -> str:
    """ヒットした行から通知の文を作る。"""
    rows = [
        f"| {entry.ng} | {'・'.join(entry.ok)}{f'（{entry.note}）' if entry.note else ''} |"
        for entry in hits
    ]
    return "\n".join([NOTICE_HEAD, *rows, NOTICE_TAIL])


if __name__ == "__main__":
    sys.exit(main())
