# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "jsonschema>=4.26.0",
#     "ruamel.yaml==0.19.1",
#     "dev-docs @ git+https://github.com/shuhei1101/dev-docs@c07f4e519568f0e93c248aa623adc1ba3e45e8d7",
# ]
# ///
"""schemas/design/ の設計書の種類のスキーマから、docs/template/markdown/ の雛形と記載例の Markdown を書き出す。

リポジトリの直下で起動する。設計書のスキーマを変えたら実行し、Markdown のテンプレートを一緒に commit する。
変換は dev-docs の schema_to_markdown を使用し、全ての種類を作ってから、違うファイルだけを書き出す。

Usage:
# Markdown のテンプレートを作り直す
uv run --frozen --script scripts/build_markdown_templates.py
# 書き出さずに、今のファイルとのずれだけを出す
uv run --frozen --script scripts/build_markdown_templates.py --check
"""

import argparse
import io
import re
import sys
import traceback
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

from build_templates import (
    DATA_KEYWORDS,
    SCHEMAS_DIR,
    TEMPLATE_IDS,
    TEMPLATES_DIR,
    BuildError,
    SchemaSet,
    load_schemas,
    resolve_ref,
)
from dev_docs.features.convert.markdown import schema_to_markdown  # pyright: ignore[reportMissingTypeStubs]
from dev_docs.features.convert.types import RenderContext  # pyright: ignore[reportMissingTypeStubs]
from dev_docs.integrations.project_index.types import IndexedDocument  # pyright: ignore[reportMissingTypeStubs]
from ruamel.yaml import YAML

from _common import DocumentError, as_list, as_mapping, load_document

if TYPE_CHECKING:
    from referencing._core import Resolver

# Markdown のテンプレートのフォルダ（リポジトリの直下からのパス）
MARKDOWN_DIR = PurePosixPath("docs/template/markdown")

# 管理用の YAML のファイル名（MARKDOWN_DIR の直下）
FILES_INDEX = "files.yaml"

# 「全ての文書の検査」の違反に出す、再生成するコマンド
COMMAND = "uv run --frozen --script scripts/build_markdown_templates.py"

# 変換の後に削除する、dev-docs の画面専用のマーカーの行
TABLE_KEY_LINE = re.compile(r"^<!-- dev-docs-table: .+ -->$")

# 管理用の YAML の先頭の行（MARKDOWN_DIR から schemas/ を指す）
_FILES_HEADER = "# yaml-language-server: $schema=../../../schemas/knowledge-files.schema.yaml\n"

# YAML のテンプレートの name の先頭（種類の名前の前に付く）
_TEMPLATE_NAME_PREFIX = "テンプレート: "

# テンプレートの ID の先頭（Markdown のファイル名から除く）
_TEMPLATE_ID_PREFIX = "template-"

# dev-docs の文書の配信元
_SOURCE_ID = "knowledge"

# 終了コード。1 = --check でずれがあった、2 = 作れなかったか想定していない例外
_EXIT_DIFFERENT = 1
_EXIT_NOT_BUILT = 2

# 変換の関数の型（種類・出力のパス・文書・スキーマから Markdown を作る）
type Convert = Callable[[str, PurePosixPath, Mapping[str, object], Mapping[str, object]], str]


@dataclass(frozen=True, slots=True)
class Output:
    """書き出す 1 ファイルの中身と、その生成元のスキーマ。"""

    # リポジトリの直下からのパス
    path: PurePosixPath
    # 書き出す中身（末尾は改行 1 つ）
    content: str
    # 生成元のスキーマ。files.yaml は全ての種類から作るので schemas/design
    schema_path: PurePosixPath


@dataclass(frozen=True, slots=True)
class TemplateMeta:
    """管理用の YAML の行へコピーする、YAML のテンプレートの値。"""

    # YAML のテンプレートの name
    name: str
    # YAML のテンプレートの description
    description: str
    # YAML のテンプレートの tags[].name の並び
    tags: tuple[str, ...]


def _use_utf8(stream: object) -> None:
    """標準出力を UTF-8 にする（Windows の既定のエンコーディングで書かない）。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """全ての種類の雛形・記載例・管理用の YAML を作ってから、書き出すか、--check ならずれを出す。"""
    parser = argparse.ArgumentParser(
        description="設計書のスキーマから、Markdown のテンプレートの雛形と記載例を書き出す"
    )
    parser.add_argument(
        "--check", action="store_true", help="書き出さずに、今のファイルとのずれを出す"
    )
    args = parser.parse_args(argv)
    check = cast("bool", args.check)
    _use_utf8(sys.stdout)

    try:
        root = Path.cwd()
        # 書き出す前に全件を作る。1 件でも失敗したら、どのファイルも書き換えない
        try:
            outputs = build_outputs(root, load_schemas(root))
        except BuildError as error:
            print(str(error), file=sys.stderr)
            return _EXIT_NOT_BUILT
        changed, stale = list_differences(root, outputs)

        # --check のとき: ずれを出すだけで、書き換えない
        if check:
            lines = [(o.path, f"{o.path}\t{o.schema_path}") for o in changed]
            lines += [(path, str(path)) for path in stale]
            for _, line in sorted(lines):
                print(line)
            return _EXIT_DIFFERENT if lines else 0

        # 書き出すとき: ずれたファイルを書き、生成の対象に無い Markdown を削除する
        for output in changed:
            target = root / output.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(output.content, encoding="utf-8", newline="\n")
        for path in stale:
            (root / path).unlink()
        for path in sorted([o.path for o in changed] + stale):
            print(path)
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返す
        traceback.print_exc()
        return _EXIT_NOT_BUILT
    return 0


def build_outputs(
    root: Path, schemas: SchemaSet, *, convert: Convert | None = None
) -> list[Output]:
    """全ての種類の雛形・記載例の Markdown と管理用の YAML を作る（Markdown はパスの昇順、最後は files.yaml）。"""
    render = convert if convert is not None else render_markdown
    markdowns: list[Output] = []
    rows: list[tuple[PurePosixPath, str, TemplateMeta]] = []
    for name, schema in schemas.docs.items():
        kind = cast("str", schema.get("x-kind"))
        template_id = TEMPLATE_IDS.get(kind)
        # 対応表に行が無いスキーマ（共通・目次）は生成しない
        if template_id is None:
            continue
        schema_path = SCHEMAS_DIR / name
        meta = _read_meta(root, template_id, schema_path)
        stem = template_id.removeprefix(_TEMPLATE_ID_PREFIX)
        inlined = cast(
            "Mapping[str, object]",
            _inline_refs(schema, schemas.registry.resolver(base_uri=name), frozenset()),
        )

        # 雛形は必ず作り、記載例はトップの examples があるときだけ最初の 1 件から作る
        documents: list[tuple[PurePosixPath, str, Mapping[str, object]]] = [
            (MARKDOWN_DIR / f"{stem}.md", "template", build_placeholder(name, schemas))
        ]
        examples = as_list(schema.get("examples")) or []
        example = as_mapping(examples[0]) if examples else None
        if example is not None:
            documents.append((MARKDOWN_DIR / f"{stem}.example.md", "example", example))

        for path, role, data in documents:
            # 変換の失敗は、どの種類で失敗したかを付けて BuildError にする
            try:
                content = render(kind, path, data, inlined)
            except Exception as error:
                raise BuildError(str(schema_path), f"変換に失敗しました: {error}") from error
            markdowns.append(Output(path, content, schema_path))
            rows.append((path, role, meta))

    markdowns.sort(key=lambda output: output.path)
    rows.sort(key=lambda row: row[0])
    index = Output(MARKDOWN_DIR / FILES_INDEX, render_files_index(rows), SCHEMAS_DIR)
    return [*markdowns, index]


def _read_meta(root: Path, template_id: str, schema_path: PurePosixPath) -> TemplateMeta:
    """対応する YAML のテンプレートから、管理用の YAML へコピーする値を読む。"""
    path = TEMPLATES_DIR / f"{template_id}.yaml"
    try:
        doc = cast("Mapping[str, object]", load_document((root / path).read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError, DocumentError) as error:
        raise BuildError(
            str(path), f"テンプレートがありません: {template_id}（{schema_path}）"
        ) from error
    tags = tuple(
        str(mapping.get("name"))
        for tag in as_list(doc.get("tags")) or []
        if (mapping := as_mapping(tag)) is not None
    )
    return TemplateMeta(
        name=str(doc.get("name", "")), description=str(doc.get("description", "")), tags=tags
    )


def _inline_refs(node: object, resolver: Resolver[Any], ancestors: frozenset[int]) -> object:
    """スキーマの全ての $ref を展開した写しを返す。再帰する $ref の先は中身を展開しない。"""
    items = as_list(node)
    if items is not None:
        return [_inline_refs(item, resolver, ancestors) for item in items]
    schema = as_mapping(node)
    if schema is None:
        return node
    merged, sub_resolver, targets = resolve_ref(schema, resolver)
    # 親が辿った先をもう一度指している: 再帰する $ref のため、子のキーと要素を展開しない
    if targets & ancestors:
        return {key: value for key, value in merged.items() if key not in ("properties", "items")}
    child_ancestors = ancestors | targets
    return {
        key: (value if key in DATA_KEYWORDS else _inline_refs(value, sub_resolver, child_ancestors))
        for key, value in merged.items()
    }


def build_placeholder(name: str, schemas: SchemaSet) -> dict[str, object]:
    """スキーマの全てのキーにプレースホルダを入れた雛形の文書を作る。"""
    schema = schemas.docs[name]
    resolver = schemas.registry.resolver(base_uri=name)
    return _placeholder_object(schema, resolver, frozenset())


def _placeholder_object(
    schema: Mapping[str, object], resolver: Resolver[Any], ancestors: frozenset[int]
) -> dict[str, object]:
    """オブジェクトのスキーマの properties を並びの順にたどり、キーごとのプレースホルダを入れる。"""
    result: dict[str, object] = {}
    for key, value in (as_mapping(schema.get("properties")) or {}).items():
        sub = as_mapping(value)
        if sub is None:
            continue
        merged, sub_resolver, targets = resolve_ref(sub, resolver)
        # 親が辿った先をもう一度指している: 再帰する $ref のため、このキーを入れない
        if targets & ancestors:
            continue
        placeholder = _placeholder_value(key, merged, sub_resolver, ancestors | targets)
        if placeholder is not None:
            result[key] = placeholder
    return result


def _placeholder_value(
    key: str,
    schema: Mapping[str, object],
    resolver: Resolver[Any],
    ancestors: frozenset[int],
) -> object | None:
    """キー 1 つのプレースホルダを決める。要素が再帰する $ref の配列は None。"""
    title = schema.get("title")
    label = title if isinstance(title, str) and title else key
    enum = as_list(schema.get("enum"))
    # 選択肢を持つ: 選択肢を ` / ` でつなぐ
    if enum:
        return " / ".join(str(choice) for choice in enum)
    kind = _type_of(schema)
    # 真偽: 取りうる値を並べる
    if kind == "boolean":
        return "true / false"
    # オブジェクト: 子のキーを同じ規則で入れる
    if kind == "object" or as_mapping(schema.get("properties")) is not None:
        return _placeholder_object(schema, resolver, ancestors)
    # 配列: 要素を 1 件だけ入れる
    if kind == "array":
        return _placeholder_array(label, schema, resolver, ancestors)
    # 文字列・数: title を波括弧で囲む
    return f"{{{label}}}"


def _placeholder_array(
    label: str,
    schema: Mapping[str, object],
    resolver: Resolver[Any],
    ancestors: frozenset[int],
) -> list[object] | None:
    """配列のキーのプレースホルダとして、要素を 1 件だけ持つ配列を作る。"""
    element = as_mapping(schema.get("items"))
    # 要素のスキーマが無い: 配列のキーの title で 1 件にする
    if element is None:
        return [f"{{{label}}}"]
    merged, element_resolver, targets = resolve_ref(element, resolver)
    # 要素が親の辿った先を指す（再帰する $ref）: このキーを入れない
    if targets & ancestors:
        return None
    element_title = merged.get("title")
    # title を持たない要素: 配列のキーの title を使用する
    if not isinstance(element_title, str) or not element_title:
        merged = {**merged, "title": label}
    value = _placeholder_value(label, merged, element_resolver, ancestors | targets)
    return None if value is None else [value]


def _type_of(schema: Mapping[str, object]) -> str | None:
    """スキーマの type を 1 つにする（配列なら null 以外の最初の型）。"""
    kind = schema.get("type")
    if isinstance(kind, str):
        return kind
    for item in as_list(kind) or []:
        if isinstance(item, str) and item != "null":
            return item
    return None


def render_markdown(
    kind: str, path: PurePosixPath, data: Mapping[str, object], schema: Mapping[str, object]
) -> str:
    """文書 1 件を dev-docs の schema_to_markdown で Markdown にし、dev-docs の画面専用の行を削除する。"""
    document = IndexedDocument(
        id=str(path),
        kind=kind,
        source_id=_SOURCE_ID,
        path=str(path),
        data=dict(data),
        # 文書に見出しのキー（title・name）が無いときは、dev-docs が metadata の name を見出しにする
        metadata={"name": path.name},
        version="",
    )
    context = RenderContext(links={}, issue_url=None, path=str(path))
    markdown = schema_to_markdown(document, cast("Mapping[str, Any]", schema), context)
    # dev-docs-table の行を削除し、続いた空行を 1 行にまとめる
    lines: list[str] = []
    for line in markdown.splitlines():
        if TABLE_KEY_LINE.match(line):
            continue
        # 前の行も空行: 空行を重ねない
        if not line.strip() and (not lines or not lines[-1].strip()):
            continue
        lines.append(line)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


def render_files_index(rows: Sequence[tuple[PurePosixPath, str, TemplateMeta]]) -> str:
    """出力した Markdown の行を持つ files.yaml の中身を作る。"""
    files: list[dict[str, object]] = []
    for path, role, meta in rows:
        kind_name = meta.name.removeprefix(_TEMPLATE_NAME_PREFIX)
        # 雛形と記載例で名前を分ける
        name = (
            f"テンプレート（Markdown）の記載例: {kind_name}"
            if role == "example"
            else f"テンプレート（Markdown）: {kind_name}"
        )
        files.append(
            {
                "path": path.name,
                "name": name,
                "description": meta.description,
                "tags": list(meta.tags),
            }
        )
    yaml = YAML(typ="rt")
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    stream = io.StringIO()
    yaml.dump({"files": files}, stream)  # pyright: ignore[reportUnknownMemberType]
    return _FILES_HEADER + stream.getvalue()


def list_differences(
    root: Path, outputs: Sequence[Output]
) -> tuple[list[Output], list[PurePosixPath]]:
    """作ったファイルと今の MARKDOWN_DIR を比べ、書き換えるファイルと削除する Markdown を返す。"""
    changed: list[Output] = []
    for output in outputs:
        target = root / output.path
        current = target.read_text(encoding="utf-8") if target.is_file() else None
        if current != output.content:
            changed.append(output)
    planned = {output.path for output in outputs}
    folder = root / MARKDOWN_DIR
    existing = sorted(folder.glob("*.md")) if folder.is_dir() else []
    stale = [MARKDOWN_DIR / p.name for p in existing if MARKDOWN_DIR / p.name not in planned]
    changed.sort(key=lambda output: output.path)
    return changed, stale


if __name__ == "__main__":
    sys.exit(main())
