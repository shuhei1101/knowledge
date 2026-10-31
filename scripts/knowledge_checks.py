# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ruamel.yaml==0.19.1",
# ]
# ///
"""標準入力の文書 1 件に、スキーマで見られない決まりを当て、違反の配列の JSON を標準出力へ出す。

dev-docs の validators の knowledge-checks。項目の ID の重複・id: の参照と related の to の実在・mermaid の文法を検査する。
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
from pathlib import Path
from typing import TYPE_CHECKING, cast

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from _common import (
    LIMIT_SEC,
    DocumentError,
    Violation,
    format_path,
    iter_strings,
    load_document,
    read_texts,
    value_line,
)
from _maid import MIN_REMAINING_SEC, MaidOutputError, find_maid, run_maid

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# 本文の [名前](id:文書の ID) と [名前](id:文書の ID#項目の ID)
ID_LINK = re.compile(r"\]\(id:([^)#\s]+)(?:#([^)\s]+))?\)")

# 行頭のバッククォート 3 つ以上と情報文字列
FENCE = re.compile(r"^ {0,3}(`{3,})\s*(\S*)")

# mermaid のブロックとして取り出す囲みのバッククォートの数。これより多い囲みは記述例として見ない
_MERMAID_TICKS = 3

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
    return [
        *check_duplicate_ids(doc),
        *check_references(doc, index),
        *check_mermaid(doc, executable, deadline),
    ]


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


if __name__ == "__main__":
    sys.exit(main())
