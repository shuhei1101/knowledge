# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ruamel.yaml==0.19.1",
# ]
# ///
"""標準入力の文書 1 件を、項目の group の階層を見出しにした mdmark の記法の Markdown にして標準出力へ出す。

dev-docs の converters の knowledge-markdown。作業ディレクトリは配信元（knowledge のリポジトリ）の直下にし、
schemas/{kind}.schema.yaml の title を種類に固有のキーの見出しに使う。

Usage:
# 文書 1 件を Markdown にする
uv run --frozen --script scripts/knowledge_markdown.py < docs/rule/dev-yaml.yaml
"""

import argparse
import io
import json
import sys
import traceback
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

from _common import DocumentError, as_list, as_mapping, load_document, load_safe

# dev-docs の画面がメタデータとして出すキー。aliases は検索の別名で、本文の読み手に役立たない
HIDDEN_KEYS = frozenset(
    {"id", "kind", "tags", "status", "visibility", "rev", "last_reviewed", "aliases"}
)

# 出す場所が決まっていて、種類に固有のキーの節にしないキー
LAYOUT_KEYS = frozenset({"name", "description", "items", "related", "sources"})

# 見出しの最も深い数
_MAX_HEADING = 6

# 項目の見出しの始まりの深さ（# {name} の 1 つ下）
_ITEM_HEADING = 2

# group の段の区切り
_GROUP_SEPARATOR = " > "

# overview の項目は見出しを付けずに description の直後へ置く
_OVERVIEW_ID = "overview"

# 表の無いセル
_EMPTY_CELL = "-"

_EXIT_FAILED = 1


def _use_utf8(stream: object) -> None:
    """標準入出力を UTF-8 にする（Windows の既定のエンコーディングで読み書きしない）。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """標準入力の文書を Markdown にして標準出力へ出す。"""
    parser = argparse.ArgumentParser(description="標準入力の文書 1 件を Markdown にして出す")
    parser.parse_args(argv)
    _use_utf8(sys.stdin)
    _use_utf8(sys.stdout)

    try:
        try:
            doc = load_document(sys.stdin.read())
        except DocumentError as error:
            print(f"{error.line} 行目: YAML として読めません: {error.message}", file=sys.stderr)
            return _EXIT_FAILED
        try:
            schema = load_schema(Path.cwd(), cast("Mapping[str, Any]", doc).get("kind"))
        except FileNotFoundError as error:
            print(error, file=sys.stderr)
            return _EXIT_FAILED
        sys.stdout.write(convert(doc, schema))
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返す
        traceback.print_exc()
        return _EXIT_FAILED
    return 0


def load_schema(root: Path, kind: object) -> Mapping[str, Any]:
    """文書の kind に当たる schemas/{kind}.schema.yaml を読む。"""
    if not isinstance(kind, str) or not kind:
        message = "文書に kind がありません"
        raise FileNotFoundError(message)
    relative = f"schemas/{kind}.schema.yaml"
    path = root / relative
    if not path.is_file():
        message = f"{relative} がありません"
        raise FileNotFoundError(message)
    schema = as_mapping(load_safe(path.read_text(encoding="utf-8")))
    return schema if schema is not None else {}


def _schema_title(schema: Mapping[str, Any], key: str) -> str:
    """スキーマの properties.{key}.title を返す。無ければキー。"""
    properties = as_mapping(schema.get("properties"))
    definition = as_mapping(properties.get(key)) if properties is not None else None
    title = definition.get("title") if definition is not None else None
    return title if isinstance(title, str) and title else key


def _related_line(row: Mapping[str, Any]) -> str:
    """related の 1 行を箇条書きの 1 行にする。"""
    to = row.get("to", "")
    line = f"- [{to}](id:{to})"
    if row.get("type"):
        line += f"（{row['type']}）"
    if row.get("when"):
        line += f": {row['when']}"
    return line


def _source_line(row: Mapping[str, Any]) -> str:
    """sources の 1 行を箇条書きの 1 行にする（id・url・note が無い行はその部分を省く）。"""
    title = row.get("title", "")
    text = f"[{title}]({row['url']})" if row.get("url") else str(title)
    if row.get("id"):
        text = f"{row['id']}: {text}"
    if row.get("note"):
        text += f"（{row['note']}）"
    return f"- {text}"


def _mappings(value: object) -> list[Mapping[str, Any]]:
    """配列のうちマッピングの要素を返す。配列でなければ空。"""
    elements = as_list(value)
    if elements is None:
        return []
    return [
        cast("Mapping[str, Any]", element) for element in elements if isinstance(element, Mapping)
    ]


def convert(doc: Mapping[str, Any], schema: Mapping[str, Any]) -> str:
    """文書を「タイトル・概要・項目・種類に固有のキー・関連・出典」の並びの Markdown にする。"""
    blocks = [f"# {doc.get('name', '')}"]
    description = doc.get("description")
    if isinstance(description, str) and description:
        blocks.append(description)

    # overview の本文は見出しを付けずに置き、残りの項目を見出しつきで並べる
    items = _mappings(doc.get("items"))
    overview = next((item for item in items if item.get("id") == _OVERVIEW_ID), None)
    if overview is not None and isinstance(overview.get("body"), str) and overview["body"]:
        blocks.append(overview["body"])
    blocks.extend(render_items([item for item in items if item is not overview]))

    # 共通のメタデータ以外のキーは、文書の並びで種類に固有の節にする
    for key, value in doc.items():
        if key in HIDDEN_KEYS or key in LAYOUT_KEYS:
            continue
        blocks.extend((f"## {_schema_title(schema, str(key))}", render_value(value)))

    if related := _mappings(doc.get("related")):
        blocks.extend(("## 関連", "\n".join(_related_line(row) for row in related)))
    if sources := _mappings(doc.get("sources")):
        blocks.extend(("## 出典", "\n".join(_source_line(row) for row in sources)))
    return "\n\n".join(blocks) + "\n"


def _heading(depth: int, text: object) -> str:
    """深さの見出しの行を作る。###### を超える深さは ###### に揃える。"""
    return f"{'#' * min(depth, _MAX_HEADING)} {text}"


def render_items(items: Sequence[Mapping[str, Any]]) -> list[str]:
    """項目を group の階層と name を見出しにしたブロックの並びにする。"""
    blocks: list[str] = []
    # 直前の項目の group の段の並び
    previous: list[str] = []
    for item in items:
        group = item.get("group")
        levels = (
            [level.strip() for level in group.split(_GROUP_SEPARATOR)]
            if isinstance(group, str) and group.strip()
            else []
        )
        # 直前の項目と先頭から一致する段は繰り返さない
        common = 0
        while common < min(len(previous), len(levels)) and previous[common] == levels[common]:
            common += 1
        blocks.extend(
            _heading(_ITEM_HEADING + depth, levels[depth]) for depth in range(common, len(levels))
        )
        # 項目の name は group の段の 1 つ下の見出し
        blocks.append(_heading(_ITEM_HEADING + len(levels), item.get("name", "")))
        body = item.get("body")
        if isinstance(body, str) and body:
            blocks.append(body)
        previous = levels
    return blocks


def _cell(value: object) -> str:
    """表のセルの文字列にする。| と改行は表を壊すので置き換える。"""
    if value is None:
        return _EMPTY_CELL
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    return text.replace("|", "\\|").replace("\n", "<br>")


def _table(rows: Sequence[Mapping[str, Any]]) -> str:
    """オブジェクトの配列を mdmark のマーカーで囲んだ表にする。"""
    # 列は全ての要素のキーを現れた順に並べる
    columns = list(dict.fromkeys(str(key) for row in rows for key in row))
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines.extend(
        "| " + " | ".join(_cell(row.get(column)) for column in columns) + " |" for row in rows
    )
    return "<!-- table: data -->\n\n" + "\n".join(lines) + "\n\n<!-- /table -->"


def render_value(value: object) -> str:
    """種類に固有のキーの値を、型に合う Markdown のブロックにする。"""
    # 文字列: そのままの段落
    if isinstance(value, str):
        return value
    elements = as_list(value)
    if elements is not None:
        rows = _mappings(elements)
        # オブジェクトの配列: 表
        if rows and len(rows) == len(elements):
            return _table(rows)
        # 文字列などの配列: 箇条書き
        return "\n".join(f"- {_inline(element)}" for element in elements)
    # オブジェクト: キーと値の箇条書き
    mapping = as_mapping(value)
    if mapping is not None:
        return "\n".join(f"- {key}: {_inline(item)}" for key, item in mapping.items())
    # 数・真偽値: その値の段落
    return str(value)


def _inline(value: object) -> str:
    """箇条書きの 1 行に置く値の文字列にする。"""
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping | list):
        return json.dumps(value, ensure_ascii=False, default=str)
    return str(value)


if __name__ == "__main__":
    sys.exit(main())
