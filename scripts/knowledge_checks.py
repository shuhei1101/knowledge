# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ruamel.yaml==0.19.1",
# ]
# ///
"""標準入力の文書 1 件に、スキーマで見られない決まりを当て、違反の配列の JSON を標準出力へ出す。

dev-docs の validators の knowledge-checks。項目の ID の重複・id: の参照と related の to の実在・aliases の衝突・文書の中の aliases の重複・mermaid の文法と、
対応表の examples が照合と合うかを検査する。
作業ディレクトリは配信元（knowledge のリポジトリ）の直下にする。

Usage:
# 文書 1 件を検査する
uv run --frozen --script scripts/knowledge_checks.py < docs/rule/dev-yaml.yaml
"""

import argparse
import io
import json
import re
import subprocess
import sys
import time
import traceback
import unicodedata
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from _common import (
    LIMIT_SEC,
    ConfigError,
    DocumentError,
    Violation,
    format_path,
    iter_strings,
    line_of,
    list_row_files,
    load_config,
    load_document,
    read_texts,
    value_line,
)
from _maid import MIN_REMAINING_SEC, MaidOutputError, find_maid, run_maid

# 対応表の照合は slop-check のフックが持つものを使う
sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "plugins/slop-check/hooks/post-tool-use")
)
from slop_check import compile_entry, entry_hits

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# 本文の [名前](id:文書の ID) と [名前](id:文書の ID#項目の ID)
ID_LINK = re.compile(r"\]\(id:([^)#\s]+)(?:#([^)\s]+))?\)")

# 行頭のバッククォート 3 つ以上と情報文字列
FENCE = re.compile(r"^ {0,3}(`{3,})\s*(\S*)")

# mermaid のブロックとして取り出す囲みのバッククォートの数。これより多い囲みは記述例として見ない
_MERMAID_TICKS = 3

# 対応表の文書の種類
_WORD_LIST_KIND = "word-list"

# maid が PATH に無いときに標準エラーへ出す理由
_MAID_MISSING = (
    "maid が PATH にありません。開発コマンドの『環境構築（クローン直後）』で maid を入れてください"
)

# 終了コード。2 = maid が無く検査を始めなかった、1 = 想定していない例外
_EXIT_MAID_MISSING = 2
_EXIT_UNEXPECTED = 1


def _use_utf8(stream: object) -> None:
    """標準入出力を UTF-8 にする（Windows の既定のエンコーディングで読み書きしない）。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None, *, limit_sec: float = LIMIT_SEC) -> int:
    """標準入力の文書を検査し、違反の配列の JSON を標準出力へ出す。"""
    deadline = time.monotonic() + limit_sec
    parser = argparse.ArgumentParser(description="標準入力の文書 1 件の違反を JSON の配列で出す")
    parser.parse_args(argv)
    _use_utf8(sys.stdin)
    _use_utf8(sys.stdout)

    # maid が無ければ検査を始めない（dev-docs が「検査を実行できませんでした」に置き換える）
    executable = find_maid()
    if executable is None:
        print(_MAID_MISSING, file=sys.stderr)
        return _EXIT_MAID_MISSING

    try:
        violations = check_document(sys.stdin.read(), Path.cwd(), executable, deadline)
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返す
        traceback.print_exc()
        return _EXIT_UNEXPECTED
    print(json.dumps(violations, ensure_ascii=False))
    return 0


def check_document(
    text: str,
    root: Path,
    executable: str,
    deadline: float,
    *,
    index: Mapping[str, frozenset[str]] | None = None,
    names: Mapping[str, Sequence[tuple[str, str]]] | None = None,
) -> list[Violation]:
    """文書 1 件に全ての検査を当て、違反を並べて返す。"""
    try:
        doc = load_document(text)
    except DocumentError as error:
        # 読めない文書は、索引を作らず maid も呼ばずに 1 件だけ返す
        return [
            {
                "path": "$",
                "rule": f"{error.line} 行目: YAML として読めません: {error.message}",
                "fix": "YAML の文法の誤りを修正する",
            }
        ]
    if index is None:
        index = build_id_index(root)
    violations = [*check_duplicate_ids(doc), *check_references(doc, index)]
    if names is None:
        try:
            names = build_name_index(root, load_config(root))
        except ConfigError as error:
            # 照合の相手を決められないので、aliases の衝突は検査せずに 1 件だけ返す
            violations.append(
                {
                    "path": "$",
                    "rule": f"1 行目: {error.message}。aliases の衝突を検査できません",
                    "fix": "配信元の直下に読める dev-docs.yaml を置く",
                }
            )
    if names is not None:
        violations.extend(check_aliases(doc, names))
    # 文書の中の重複は dev-docs.yaml を使用しないので、名前の索引の有無によらず適用する
    violations.extend(check_alias_duplicates(doc))
    violations.extend(check_mermaid(doc, executable, deadline))
    # 対応表は examples の検査を後ろにつなぐ
    if _field(doc, "kind") == _WORD_LIST_KIND:
        violations.extend(check_word_list(doc))
    return violations


def _field(node: CommentedMap, key: str) -> object:
    """マッピングのキーの値を返す。無ければ None。"""
    return cast("Mapping[str, object]", node).get(key)


def _rows(node: CommentedMap, key: str) -> list[tuple[int, CommentedMap]]:
    """キーの値の配列のうち、マッピングの要素を添字と並べて返す。配列でなければ空。"""
    value = _field(node, key)
    if not isinstance(value, CommentedSeq):
        return []
    return [
        (position, row)
        for position, row in enumerate(cast("list[object]", value))
        if isinstance(row, CommentedMap)
    ]


def _item_ids(doc: CommentedMap) -> frozenset[str]:
    """文書の items[].id の集合を返す。"""
    return frozenset(
        item_id for _, item in _rows(doc, "items") if isinstance(item_id := _field(item, "id"), str)
    )


def build_id_index(root: Path) -> dict[str, frozenset[str]]:
    """配信元の全ての文書から、文書の ID → 項目の ID の索引を作る。"""
    paths = sorted(root.glob("docs/**/*.yaml"))
    index: dict[str, frozenset[str]] = {}
    for text in read_texts(paths).values():
        # 読めないファイル・文書は飛ばす（その文書の誤りはその文書の検査で出る）
        if text is None:
            continue
        try:
            doc = load_document(text)
        except DocumentError:
            continue
        doc_id = _field(doc, "id")
        if isinstance(doc_id, str):
            index[doc_id] = _item_ids(doc)
    return index


def normalize_name(value: str) -> str:
    """照合の前に、名前へ NFKC・前後の空白の除去・英字の大文字小文字の統一を適用する。"""
    return unicodedata.normalize("NFKC", value).strip().casefold()


def build_name_index(
    root: Path, rows: Sequence[Mapping[str, Any]]
) -> dict[str, list[tuple[str, str]]]:
    """alias_type を持つ行の文書（records の行は要素）から、正規化した名前 → （ID、name か aliases）の索引を作る。"""
    # ファイルごとに、行の records（要素を並べたキー）を控える
    records: dict[Path, str | None] = {}
    for row in rows:
        if row.get("alias_type") is None:
            continue
        key = row.get("records")
        for file in list_row_files(root, row):
            records.setdefault(root / file, key if isinstance(key, str) else None)
    names: dict[str, list[tuple[str, str]]] = {}
    for path, text in read_texts(sorted(records)).items():
        # 読めないファイル・文書は飛ばす（その文書の誤りはその文書の検査で出る）
        if text is None:
            continue
        try:
            doc = load_document(text)
        except DocumentError:
            continue
        for entry in _match_entries(doc, records[path]):
            _add_names(names, entry)
    return names


def _add_names(names: dict[str, list[tuple[str, str]]], entry: CommentedMap) -> None:
    """照合の相手 1 件の name と aliases を、正規化したキーで索引に加える。id の無い相手は飛ばす。"""
    entry_id = _field(entry, "id")
    if not isinstance(entry_id, str):
        return
    name = _field(entry, "name")
    if isinstance(name, str):
        names.setdefault(normalize_name(name), []).append((entry_id, "name"))
    for alias in _aliases(entry):
        names.setdefault(normalize_name(alias), []).append((entry_id, "aliases"))


def _match_entries(doc: CommentedMap, key: str | None) -> list[CommentedMap]:
    """照合の相手を返す。records の無い行は文書そのもの、ある行は records のキーの配列の要素。"""
    if key is None:
        return [doc]
    value = _field(doc, key)
    # records のキーの値が配列でなければ、そのファイルを飛ばす
    if not isinstance(value, CommentedSeq):
        return []
    return [entry for entry in cast("list[object]", value) if isinstance(entry, CommentedMap)]


def _aliases(doc: CommentedMap) -> list[str]:
    """aliases の文字列の要素を返す。配列でなければ空。"""
    value = _field(doc, "aliases")
    if not isinstance(value, CommentedSeq):
        return []
    return [alias for alias in cast("list[object]", value) if isinstance(alias, str)]


def check_aliases(
    doc: CommentedMap, names: Mapping[str, Sequence[tuple[str, str]]]
) -> list[Violation]:
    """aliases の要素が、ほかの文書の name・aliases と正規化して一致したら違反にする。"""
    value = _field(doc, "aliases")
    if not isinstance(value, CommentedSeq):
        return []
    doc_id = _field(doc, "id")
    violations: list[Violation] = []
    for position, alias in enumerate(cast("list[object]", value)):
        if not isinstance(alias, str):
            continue
        # 書き込む前の自分の値は照合の相手にしない
        owners = [
            (owner, field)
            for owner, field in names.get(normalize_name(alias), [])
            if owner != doc_id
        ]
        if not owners:
            continue
        others = "、".join(f"`{owner}` の {field}" for owner, field in owners)
        line = line_of(doc, ["aliases", position])
        violations.append(
            {
                "path": f"aliases[{position}]",
                "rule": f"{line} 行目: 別名 `{alias}` が {others} と衝突しています",
                "fix": "指す文書を 1 件に決め、片方だけに登録する",
            }
        )
    return violations


def check_alias_duplicates(doc: CommentedMap) -> list[Violation]:
    """aliases の要素が、自分の name か前の要素と正規化して一致したら違反にする。"""
    value = _field(doc, "aliases")
    if not isinstance(value, CommentedSeq):
        return []
    # name が文字列でなければ記録せず、前の要素だけと照合する
    name = _field(doc, "name")
    own_name = normalize_name(name) if isinstance(name, str) else None
    # 正規化した値 → 最初に出た要素の添字
    first: dict[str, int] = {}
    violations: list[Violation] = []
    for position, alias in enumerate(cast("list[object]", value)):
        # 文字列でない要素は照合の相手にも入れない
        if not isinstance(alias, str):
            continue
        key = normalize_name(alias)
        line = line_of(doc, ["aliases", position])
        # 自分の name と一致: 前の要素とも一致していても name との一致の 1 件にする
        if key == own_name:
            violations.append(
                {
                    "path": f"aliases[{position}]",
                    "rule": f"{line} 行目: 別名 `{alias}` が name と同じです",
                    "fix": "片方だけ登録する",
                }
            )
        # 前の要素と一致: 最初に出た要素の添字を示す
        elif key in first:
            violations.append(
                {
                    "path": f"aliases[{position}]",
                    "rule": f"{line} 行目: 別名 `{alias}` が aliases[{first[key]}] と重複しています",
                    "fix": "片方だけ登録する",
                }
            )
        # どちらとも一致しない: 前の要素として記録する
        else:
            first[key] = position
    return violations


def check_duplicate_ids(doc: CommentedMap) -> list[Violation]:
    """items[].id の重複を、後に出た項目の違反にする。"""
    # 項目の ID → 最初に出た添字
    first: dict[str, int] = {}
    violations: list[Violation] = []
    for position, item in _rows(doc, "items"):
        item_id = _field(item, "id")
        if not isinstance(item_id, str):
            continue
        # 先に出た ID と同じ: 後の項目を違反にする
        if item_id in first:
            line = value_line(item, "id")
            violations.append(
                {
                    "path": format_path(["items", position, "id"]),
                    "rule": f"{line} 行目: 項目の ID `{item_id}` が items[{first[item_id]}] と重複しています",
                    "fix": "項目の ID を文書の中で一意にする",
                }
            )
        else:
            first[item_id] = position
    return violations


def check_references(doc: CommentedMap, index: Mapping[str, frozenset[str]]) -> list[Violation]:
    """本文の id: の参照と related[].to が実在する文書・項目を指すかを確かめる。"""
    # 自分を指す参照は、索引ではなく標準入力の内容で確かめる
    known = dict(index)
    doc_id = _field(doc, "id")
    if isinstance(doc_id, str):
        known[doc_id] = _item_ids(doc)

    violations: list[Violation] = []
    for parts, first_line, value in iter_strings(doc):
        fenced = _fenced_lines(value)
        for match in ID_LINK.finditer(value):
            target_doc, target_item = match.group(1), match.group(2)
            offset = value.count("\n", 0, match.start())
            # コードブロックの中の参照は記述例なので見ない
            if offset in fenced:
                continue
            # 本文の 1 行目の行に、一致の前にある改行の数を足した行
            line = first_line + offset
            # 文書が無い
            if target_doc not in known:
                violations.append(
                    {
                        "path": format_path(parts),
                        "rule": f"{line} 行目: 参照先の文書 `{target_doc}` がありません",
                        "fix": "実在する文書の ID を指す",
                    }
                )
            # 文書はあるが、指した項目が無い
            elif target_item is not None and target_item not in known[target_doc]:
                violations.append(
                    {
                        "path": format_path(parts),
                        "rule": f"{line} 行目: 参照先の項目 `{target_doc}#{target_item}` がありません",
                        "fix": "実在する項目の ID を指す",
                    }
                )

    for position, row in _rows(doc, "related"):
        to = _field(row, "to")
        if isinstance(to, str) and to not in known:
            violations.append(
                {
                    "path": format_path(["related", position, "to"]),
                    "rule": f"{value_line(row, 'to')} 行目: 関連先の文書 `{to}` がありません",
                    "fix": "実在する文書の ID を指す",
                }
            )
    return violations


def _fenced_lines(text: str) -> frozenset[int]:
    """文字列のうち、コードブロックの囲みの中と囲みの行の位置（0 始まり）を返す。"""
    fenced: set[int] = set()
    # 開いている囲みのバッククォートの数。0 は囲みの外
    open_ticks = 0
    for position, line in enumerate(text.split("\n")):
        matched = FENCE.match(line)
        # 囲みの外: 囲みを開く行なら、開いた数を覚える
        if open_ticks == 0:
            if matched:
                open_ticks = len(matched.group(1))
                fenced.add(position)
            continue
        fenced.add(position)
        # 囲みの中: 開いた数以上のバッククォートで情報文字列の無い行で閉じる
        if matched and len(matched.group(1)) >= open_ticks and not matched.group(2):
            open_ticks = 0
    return frozenset(fenced)


def mermaid_blocks(text: str) -> list[tuple[int, str]]:
    """文字列から mermaid のコードブロックを、中身の 1 行目の位置（0 始まり）と中身で取り出す。"""
    blocks: list[tuple[int, str]] = []
    # 開いている囲みのバッククォートの数。0 は囲みの外
    open_ticks = 0
    collecting = False
    start = 0
    lines: list[str] = []
    for position, line in enumerate(text.split("\n")):
        matched = FENCE.match(line)
        # 囲みの外: 囲みを開く行かを見る
        if open_ticks == 0:
            if matched:
                open_ticks = len(matched.group(1))
                # バッククォート 3 つの mermaid だけを取り出す。4 つ以上の囲みの中は記述例なので見ない
                collecting = open_ticks == _MERMAID_TICKS and matched.group(2) == "mermaid"
                start = position + 1
                lines = []
            continue
        # 囲みの中: 開いた数以上のバッククォートで情報文字列の無い行で閉じる
        if matched and len(matched.group(1)) >= open_ticks and not matched.group(2):
            if collecting:
                blocks.append((start, "\n".join(lines)))
            open_ticks = 0
            collecting = False
            continue
        if collecting:
            lines.append(line)
    # 閉じずに終わった mermaid のブロックは末尾までを中身にする
    if collecting:
        blocks.append((start, "\n".join(lines)))
    return blocks


def _timeout_violation(path: str, line: int) -> Violation:
    """maid を呼べなかった・打ち切ったブロックの時間切れの違反を作る。"""
    return {
        "path": path,
        "rule": f"{line} 行目: mermaid: 処理時間の上限に達したため検査していません",
        "fix": "図の数を減らすか、文書を分ける",
    }


def check_mermaid(doc: CommentedMap, executable: str, deadline: float) -> list[Violation]:
    """文書の中の mermaid のブロックを 1 つずつ maid で検査し、誤りと時間切れを違反にする。"""
    violations: list[Violation] = []
    for parts, first_line, value in iter_strings(doc):
        path = format_path(parts)
        for position, diagram in mermaid_blocks(value):
            block_line = first_line + position
            remaining = deadline - time.monotonic()
            # 残り時間が足りない: maid を呼ばずに時間切れにする
            if remaining < MIN_REMAINING_SEC:
                violations.append(_timeout_violation(path, block_line))
                continue
            try:
                findings = run_maid(executable, diagram, remaining)
            except subprocess.TimeoutExpired:
                violations.append(_timeout_violation(path, block_line))
                continue
            except MaidOutputError as error:
                violations.append(
                    {
                        "path": path,
                        "rule": f"{block_line} 行目: mermaid: {error.message}",
                        "fix": "開発コマンドの環境構築で入れた maid のバージョンを確かめる",
                    }
                )
                continue
            # maid の行は図の中の行（1 始まり）なので、ブロックの文書の行へ戻す
            violations.extend(
                {
                    "path": path,
                    "rule": f"{block_line + finding.line - 1} 行目: mermaid: {finding.message}",
                    "fix": "mermaid の文法の誤りを修正する",
                }
                for finding in findings
            )
    return violations


def _examples(entry: CommentedMap, key: str) -> list[tuple[int, str]]:
    """examples の hit か pass の文を添字と並べて返す。無ければ空。"""
    examples = _field(entry, "examples")
    if not isinstance(examples, CommentedMap):
        return []
    values = _field(examples, key)
    if not isinstance(values, CommentedSeq):
        return []
    return [
        (position, value)
        for position, value in enumerate(cast("list[object]", values))
        if isinstance(value, str)
    ]


def check_word_list(doc: CommentedMap) -> list[Violation]:
    """対応表の各行の照合を examples の hit と pass に当て、合わないものを違反にする。"""
    violations: list[Violation] = []
    for position, entry in _rows(doc, "entries"):
        try:
            matcher = compile_entry(cast("Mapping[str, object]", entry))
        except re.error as error:
            # 読めない正規表現: その行の examples は当てない
            line = line_of(doc, ["entries", position, "pattern"])
            violations.append(
                {
                    "path": format_path(["entries", position, "pattern"]),
                    "rule": f"{line} 行目: 正規表現として読めません: {error}",
                    "fix": "Python の re で読める正規表現にする",
                }
            )
            continue
        # hit の文: ヒットしなければ違反
        for index, example in _examples(entry, "hit"):
            if not entry_hits(example, matcher):
                parts = ["entries", position, "examples", "hit", index]
                violations.append(
                    {
                        "path": format_path(parts),
                        "rule": f"{line_of(doc, parts)} 行目: 「{example}」にヒットしません",
                        "fix": "pattern を修正するか、hit の例を修正する",
                    }
                )
        # pass の文: ヒットすれば違反
        for index, example in _examples(entry, "pass"):
            if entry_hits(example, matcher):
                parts = ["entries", position, "examples", "pass", index]
                violations.append(
                    {
                        "path": format_path(parts),
                        "rule": f"{line_of(doc, parts)} 行目: 「{example}」にヒットします",
                        "fix": "pattern か allow を修正するか、pass の例を修正する",
                    }
                )
    return violations


if __name__ == "__main__":
    sys.exit(main())
