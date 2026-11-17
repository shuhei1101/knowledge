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
import re
import sys
import traceback
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, cast

from _common import (
    ConfigError,
    DocumentError,
    as_list,
    as_mapping,
    list_row_files,
    load_config,
    load_document,
    load_safe,
)

# dev-docs の画面がメタデータとして出すキー。aliases は検索の別名、inject_when は alias-inject の照合条件で、
# 本文の読み手に役立たない
HIDDEN_KEYS = frozenset(
    {
        "id",
        "kind",
        "tags",
        "status",
        "visibility",
        "rev",
        "last_reviewed",
        "aliases",
        "inject_when",
    }
)

# 出す場所が決まっていて、種類に固有のキーの節にしないキー
LAYOUT_KEYS = frozenset({"name", "description", "items", "related", "sources"})

# entries を NG・OK の表にする文書の kind
WORD_LIST_KIND = "word-list"

# 対応表の entries のキー
_WORD_LIST_ENTRIES = "entries"

# 埋め込む対応表のファイルを引く project-index.yaml の documents[] の行の id
WORD_LIST_ROW = "word-list"

# 埋め込みのマーカー。/・# を含む dev-docs のパスの書き方には当たらない
EMBED_MARKER = re.compile(r"<!--\s*embed:\s*(?P<id>[^\s/#]+)\s*-->")

# コードブロックの開きと閉じ
FENCE = re.compile(r"^\s{0,3}(?P<mark>`{3,}|~{3,})")

# 文書の ID から対応表の entries への対応
type WordLists = Mapping[str, Sequence[Mapping[str, Any]]]

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

# スキーマの中を指す $ref の頭
_LOCAL_REF = "#/"

# 箇条書きの 1 段の字下げ
_INDENT = "  "

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
        # マーカーのある文書だけ対応表を読む
        try:
            word_lists = load_word_lists(Path.cwd()) if has_embed(doc) else {}
        except ConfigError as error:
            print(error.message, file=sys.stderr)
            return _EXIT_FAILED
        sys.stdout.write(convert(doc, schema, word_lists))
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


def resolve_definition(
    schema: Mapping[str, Any], definition: Mapping[str, Any] | None, key: str | None
) -> Mapping[str, Any] | None:
    """親の定義から、キーか配列の要素の定義を、スキーマの中の $ref を解決して返す。"""
    if definition is None:
        return None
    # key があれば properties の子、無ければ配列の items
    if key is not None:
        properties = as_mapping(definition.get("properties"))
        child = as_mapping(properties.get(key)) if properties is not None else None
    else:
        child = as_mapping(definition.get("items"))
    if child is None:
        return None
    return _resolve_ref(schema, child)


def _resolve_ref(schema: Mapping[str, Any], definition: Mapping[str, Any]) -> Mapping[str, Any]:
    """定義の $ref を参照先に置き換え、$ref 以外の兄弟のキーを上に重ねる。"""
    resolved = dict(definition)
    seen: set[str] = set()
    while "$ref" in resolved:
        ref = resolved.pop("$ref")
        # 別のファイル・たどった参照・たどれない参照は解決せず、兄弟のキーだけを残す
        if not isinstance(ref, str) or not ref.startswith(_LOCAL_REF) or ref in seen:
            break
        seen.add(ref)
        target = _follow_pointer(schema, ref)
        if target is None:
            break
        # 兄弟のキー（title など）を参照先より優先する
        resolved = {**target, **resolved}
    return resolved


def _follow_pointer(schema: Mapping[str, Any], ref: str) -> Mapping[str, Any] | None:
    """#/ で始まる参照のパスを、スキーマの中のマッピングまでたどる。"""
    node: Mapping[str, Any] | None = schema
    for part in ref.removeprefix(_LOCAL_REF).split("/"):
        if node is None:
            return None
        # JSON Pointer の ~1 は /、~0 は ~
        node = as_mapping(node.get(part.replace("~1", "/").replace("~0", "~")))
    return node


def _title(definition: Mapping[str, Any] | None, key: str) -> str:
    """定義の title を返す。無ければキー。"""
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


def convert(doc: Mapping[str, Any], schema: Mapping[str, Any], word_lists: WordLists) -> str:
    """文書を「タイトル・概要・項目・種類に固有のキー・関連・出典」の並びの Markdown にする。"""
    blocks = [f"# {doc.get('name', '')}"]
    description = doc.get("description")
    if isinstance(description, str) and description:
        blocks.append(description)

    # overview の本文は見出しを付けずに置き、残りの項目を見出しつきで並べる
    items = _mappings(doc.get("items"))
    overview = next((item for item in items if item.get("id") == _OVERVIEW_ID), None)
    if overview is not None and isinstance(overview.get("body"), str) and overview["body"]:
        blocks.append(expand_embeds(overview["body"], word_lists))
    blocks.extend(render_items([item for item in items if item is not overview], word_lists))

    # 共通のメタデータ以外のキーは、文書の並びで種類に固有の節にする
    for key, value in doc.items():
        if key in HIDDEN_KEYS or key in LAYOUT_KEYS:
            continue
        # キーの定義はスキーマ自身を起点に解決する。対応表の行は照合の値を出さずに NG・OK の表にする
        definition = resolve_definition(schema, schema, str(key))
        if doc.get("kind") == WORD_LIST_KIND and key == _WORD_LIST_ENTRIES:
            block = render_word_list(_mappings(value))
        else:
            block = render_value(value, definition, schema)
        blocks.extend((f"## {_title(definition, str(key))}", block))

    if related := _mappings(doc.get("related")):
        blocks.extend(("## 関連", "\n".join(_related_line(row) for row in related)))
    if sources := _mappings(doc.get("sources")):
        blocks.extend(("## 出典", "\n".join(_source_line(row) for row in sources)))
    return "\n\n".join(blocks) + "\n"


def _heading(depth: int, text: object) -> str:
    """深さの見出しの行を作る。###### を超える深さは ###### に揃える。"""
    return f"{'#' * min(depth, _MAX_HEADING)} {text}"


def render_items(items: Sequence[Mapping[str, Any]], word_lists: WordLists) -> list[str]:
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
            blocks.append(expand_embeds(body, word_lists))
        previous = levels
    return blocks


def _is_scalar(value: object) -> bool:
    """配列・オブジェクトでない値か。"""
    return as_list(value) is None and as_mapping(value) is None


def _scalar(value: object) -> str:
    """文字列・数・真偽値を文字列にする。"""
    return value if isinstance(value, str) else str(value)


def _cell_text(
    value: object, definition: Mapping[str, Any] | None, schema: Mapping[str, Any]
) -> str:
    """セルの値を、配列は要素、オブジェクトは {title}: {値} を <br> でつないだ文字列にする。"""
    elements = as_list(value)
    if elements is not None:
        item_definition = resolve_definition(schema, definition, None)
        return "<br>".join(_cell_text(element, item_definition, schema) for element in elements)
    mapping = as_mapping(value)
    if mapping is not None:
        parts: list[str] = []
        for key, item in mapping.items():
            child = resolve_definition(schema, definition, str(key))
            parts.append(f"{_title(child, str(key))}: {_cell_text(item, child, schema)}")
        return "<br>".join(parts)
    return _scalar(value)


def _cell(value: object, definition: Mapping[str, Any] | None, schema: Mapping[str, Any]) -> str:
    """表のセルの文字列にする。| と改行は表を壊すので置き換える。"""
    if value is None:
        return _EMPTY_CELL
    text = _cell_text(value, definition, schema)
    return text.replace("|", "\\|").replace("\n", "<br>")


def _table(
    rows: Sequence[Mapping[str, Any]],
    definition: Mapping[str, Any] | None,
    schema: Mapping[str, Any],
) -> str:
    """オブジェクトの配列を、列名を要素の定義の title にした mdmark のマーカーで囲んだ表にする。"""
    item_definition = resolve_definition(schema, definition, None)
    # 列は全ての要素のキーを現れた順に並べる
    columns = list(dict.fromkeys(str(key) for row in rows for key in row))
    column_definitions = {
        column: resolve_definition(schema, item_definition, column) for column in columns
    }
    lines = [
        "| " + " | ".join(_title(column_definitions[column], column) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines.extend(
        "| "
        + " | ".join(
            _cell(row.get(column), column_definitions[column], schema) for column in columns
        )
        + " |"
        for row in rows
    )
    return '<!-- table: {"kind": "data"} -->\n\n' + "\n".join(lines) + "\n\n<!-- /table -->"


def _list_lines(
    value: object, definition: Mapping[str, Any] | None, schema: Mapping[str, Any], depth: int
) -> list[str]:
    """配列・オブジェクトを、深さごとに字下げした箇条書きの行にする。"""
    indent = _INDENT * depth
    lines: list[str] = []
    mapping = as_mapping(value)
    # オブジェクト: キーごとに title の行。入れ子の値はその下に 1 段下げる
    if mapping is not None:
        for key, item in mapping.items():
            child = resolve_definition(schema, definition, str(key))
            title = _title(child, str(key))
            if _is_scalar(item):
                lines.append(f"{indent}- {title}: {_scalar(item)}")
            else:
                lines.append(f"{indent}- {title}")
                lines.extend(_list_lines(item, child, schema, depth + 1))
        return lines
    # 配列: 要素ごとの行。入れ子の要素は、定義の title か - だけの行の下に 1 段下げる
    item_definition = resolve_definition(schema, definition, None)
    for element in as_list(value) or []:
        if _is_scalar(element):
            lines.append(f"{indent}- {_scalar(element)}")
            continue
        title = item_definition.get("title") if item_definition is not None else None
        lines.append(f"{indent}- {title}" if isinstance(title, str) and title else f"{indent}-")
        lines.extend(_list_lines(element, item_definition, schema, depth + 1))
    return lines


def render_value(
    value: object, definition: Mapping[str, Any] | None, schema: Mapping[str, Any]
) -> str:
    """種類に固有のキーの値を、型とスキーマの定義に合う Markdown のブロックにする。"""
    # 文字列: そのままの段落
    if isinstance(value, str):
        return value
    elements = as_list(value)
    if elements is not None:
        rows = _mappings(elements)
        # 全ての要素がオブジェクトの配列: 表
        if rows and len(rows) == len(elements):
            return _table(rows, definition, schema)
    # それ以外の配列とオブジェクト: 箇条書き
    if not _is_scalar(value):
        return "\n".join(_list_lines(value, definition, schema, 0))
    # 数・真偽値: その値の段落
    return str(value)


def render_word_list(entries: Sequence[Mapping[str, Any]]) -> str:
    """対応表の entries を、slop-check の通知と同じ書式の NG・OK の表にする。"""
    lines = ["| NG | OK |", "| --- | --- |"]
    for entry in entries:
        ok = "・".join(str(word) for word in as_list(entry.get("ok")) or [])
        if entry.get("note"):
            ok += f"（{entry['note']}）"
        # 対応表の値は文字列だけで、スキーマの定義を使わない
        lines.append(f"| {_cell(entry.get('ng'), None, {})} | {_cell(ok, None, {})} |")
    return '<!-- table: {"kind": "data"} -->\n\n' + "\n".join(lines) + "\n\n<!-- /table -->"


def _outside_fences(body: str) -> Iterator[tuple[int, str]]:
    """本文の行のうちコードブロックの外の行を、行の位置と行の組で返す。"""
    fence: str | None = None
    for index, line in enumerate(body.split("\n")):
        opened = FENCE.match(line)
        if fence is None and opened:
            # コードブロックの開き
            fence = opened.group("mark")
        elif fence is not None:
            # 開きと同じ文字で、開き以上の長さの行で閉じる
            if (
                opened
                and opened.group("mark")[0] == fence[0]
                and len(opened.group("mark")) >= len(fence)
            ):
                fence = None
        else:
            yield index, line


def _embed_id(line: str) -> str | None:
    """行が埋め込みのマーカーだけなら、指す文書の ID を返す。"""
    matched = EMBED_MARKER.fullmatch(line.strip())
    return matched.group("id") if matched else None


def has_embed(doc: Mapping[str, Any]) -> bool:
    """項目の本文のどれかが、コードブロックの外に埋め込みのマーカーの行を持つかを返す。"""
    for item in _mappings(doc.get("items")):
        body = item.get("body")
        if isinstance(body, str) and any(
            _embed_id(line) is not None for _, line in _outside_fences(body)
        ):
            return True
    return False


def load_word_lists(root: Path) -> dict[str, list[Mapping[str, Any]]]:
    """project-index.yaml の word-list の行の対応表を読み、文書の ID から entries への対応にする。"""
    row = next((row for row in load_config(root) if row.get("id") == WORD_LIST_ROW), None)
    if row is None:
        return {}
    word_lists: dict[str, list[Mapping[str, Any]]] = {}
    for relative in list_row_files(root, row):
        try:
            doc = load_document((root / relative).read_text(encoding="utf-8"))
        except DocumentError as error:
            message = f"{relative} の {error.line} 行目が読めません: {error.message}"
            raise ConfigError(message) from error
        # 対応表の種類の文書だけを ID で引けるようにする
        mapping = cast("Mapping[str, Any]", doc)
        if mapping.get("kind") == WORD_LIST_KIND and isinstance(mapping.get("id"), str):
            word_lists[mapping["id"]] = _mappings(mapping.get(_WORD_LIST_ENTRIES))
    return word_lists


def expand_embeds(body: str, word_lists: WordLists) -> str:
    """本文のコードブロックの外の埋め込みのマーカーの行を、対応表の表か注意書きに置き換える。"""
    lines = body.split("\n")
    for index, line in _outside_fences(body):
        target = _embed_id(line)
        if target is None:
            continue
        # ID の対応表があれば表、無ければ展開できない理由の注意書き
        entries = word_lists.get(target)
        lines[index] = (
            render_word_list(entries)
            if entries is not None
            else f"> [!WARNING]\n> 埋め込めません: {target} の対応表がありません"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
