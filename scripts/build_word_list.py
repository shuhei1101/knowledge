# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ruamel.yaml==0.19.1",
# ]
# ///
"""正本の対応表の YAML から、プラグイン slop-check のフックが読む JSON のコピーを書き出す。

リポジトリの直下で起動する。正本の対応表を変えたら実行し、コピーを一緒に commit する。

Usage:
# 対応表のコピーを作り直す
uv run --frozen --script scripts/build_word_list.py
"""

import argparse
import json
import sys
import traceback
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, cast

from ruamel.yaml.comments import CommentedMap, CommentedSeq

from _common import DocumentError, load_document

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# リポジトリの直下からの正本の対応表とコピーのパス
SOURCE = PurePosixPath("docs/word-list/word-list-ai-slop.yaml")
COPY = PurePosixPath("plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json")

# コピーの entries[] の各行に残すキーとその順
COPY_KEYS = ("id", "ng", "ok", "pattern", "allow", "note")

# 終了コード。2 = 正本が読めずコピーを書き換えなかった、1 = 想定していない例外
_EXIT_SOURCE_UNREADABLE = 2
_EXIT_UNEXPECTED = 1


def main(argv: Sequence[str] | None = None) -> int:
    """正本を読み、コピーを書き出して終了コードを返す。"""
    parser = argparse.ArgumentParser(description="対応表の正本から slop-check が読むコピーを作る")
    parser.parse_args(argv)

    try:
        root = Path.cwd()
        # 正本が読めないときは、前回のコピーを残す
        try:
            doc = load_document((root / SOURCE).read_text(encoding="utf-8"))
        except (OSError, DocumentError) as error:
            print(f"対応表を読めません: {SOURCE}: {error}", file=sys.stderr)
            return _EXIT_SOURCE_UNREADABLE
        (root / COPY).write_text(render_copy(doc), encoding="utf-8", newline="\n")
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返す
        traceback.print_exc()
        return _EXIT_UNEXPECTED
    return 0


def _plain(value: object) -> object:
    """ruamel.yaml の配列を JSON に書ける list にする。"""
    if isinstance(value, CommentedSeq):
        return [_plain(item) for item in cast("list[object]", value)]
    return value


def render_copy(doc: CommentedMap) -> str:
    """読んだ正本から、コピーの JSON の文字列を作る。"""
    rows: list[dict[str, object]] = []
    entries = cast("Mapping[str, object]", doc).get("entries")
    if isinstance(entries, CommentedSeq):
        for entry in cast("list[object]", entries):
            if not isinstance(entry, CommentedMap):
                continue
            mapping = cast("Mapping[str, object]", entry)
            # 残すキーだけを固定の順で、値があるものだけ取り出す
            rows.append(
                {key: _plain(mapping[key]) for key in COPY_KEYS if mapping.get(key) is not None}
            )
    return json.dumps({"entries": rows}, ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":
    sys.exit(main())
