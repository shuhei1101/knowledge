# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "jsonschema>=4.26.0",
#     "ruamel.yaml==0.19.1",
# ]
# ///
"""schemas/design/ の設計書の種類のスキーマから、docs/template/ の対応するテンプレートの items を書き出す。

リポジトリの直下で起動する。設計書のスキーマを変えたら実行し、テンプレートを一緒に commit する。
全てのスキーマとテンプレートを読み、全件の items を組み立ててから、違うものだけを書き出す。

Usage:
# 設計書のテンプレートを作り直す
uv run --frozen --script scripts/build_templates.py
"""

import argparse
import io
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import YAMLError
from ruamel.yaml.scalarstring import LiteralScalarString

from _common import DocumentError, as_list, as_mapping, load_document, load_safe

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping, Sequence

    from referencing._core import Resolver

# リポジトリの直下からの設計書のスキーマとテンプレートのフォルダ
SCHEMAS_DIR = PurePosixPath("schemas/design")
TEMPLATES_DIR = PurePosixPath("docs/template")

# スキーマの x-kind → テンプレートの ID
TEMPLATE_IDS = {
    "architecture": "template-architecture",
    "component": "template-component",
    "config": "template-config",
    "dataflow": "template-dataflow",
    "dev_command": "template-dev-command",
    "er": "template-er",
    "external_api": "template-external-api",
    "interface": "template-interface",
    "library": "template-external-library",
    "module": "template-module",
    "nonfunctional": "template-nonfunctional",
    "scenario": "template-scenario",
    "screen": "template-screen-design",
    "state_transition": "template-state-transition",
    "test_procedure": "template-test-procedure",
}

# キーの表の制約の列に、この順で出すキーワード
CONSTRAINT_KEYS = (
    "const",
    "pattern",
    "format",
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
    "minimum",
    "maximum",
)

# 標準エラーと全ての文書の検査の違反に出す、生成し直すコマンド
COMMAND = "uv run --frozen --script scripts/build_templates.py"

# 値の中がスキーマではないキーワード（$ref の確認で辿らない）
_DATA_KEYWORDS = frozenset({"examples", "enum", "const", "default", "x-bad-examples"})

# 値が「名前 → スキーマ」の対応のキーワード
_NAMED_SCHEMA_KEYWORDS = frozenset({"properties", "patternProperties", "$defs", "dependentSchemas"})

# 表の列
_KEY_TABLE_COLUMNS = ("名前", "title", "型", "必須", "選択肢", "制約", "description", "examples")
_KEY_RULES_COLUMNS = ("名前", "決まり", "悪い例", "理由")

# 表の範囲のマーカー
_TABLE_OPEN = "<!-- table: data -->"
_TABLE_CLOSE = "<!-- /table -->"

# 終了コード。2 = スキーマかテンプレートが読めずどのファイルも書き換えなかった、1 = 想定していない例外
_EXIT_NOT_BUILT = 2
_EXIT_UNEXPECTED = 1


@dataclass(frozen=True, slots=True)
class KeyRow:
    """キーの表とキーごとの決まりの表の 1 行になる、$ref を解決したキー 1 つ。"""

    # parent.child・parent[].child の名前
    name: str
    # $ref を解決した先のキーのスキーマに、キーの側の値を重ねたもの
    schema: Mapping[str, object]
    # 親の required に名前があるか
    required: bool


@dataclass(frozen=True, slots=True)
class SchemaSet:
    """schemas/design/ の全てのスキーマと、ファイル名を URI にした $ref の登録。"""

    # ファイル名 → スキーマ（ファイル名の順）
    docs: dict[str, Mapping[str, object]]
    # ファイル名を URI にして全てのスキーマを登録したもの
    registry: Registry[Any]


class BuildError(Exception):
    """スキーマかテンプレートが読めず、生成を始められない理由。"""

    def __init__(self, path: str, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        # 原因のファイルのリポジトリの直下からのパス
        self.path = path
        # 理由
        self.reason = reason


def _use_utf8(stream: object) -> None:
    """標準出力を UTF-8 にする（Windows の既定のエンコーディングで書かない）。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """全てのスキーマとテンプレートを読み、全件の items を組み立ててから、違うものだけ書き出す。"""
    parser = argparse.ArgumentParser(
        description="設計書のスキーマから、対応するテンプレートの items を書き出す"
    )
    parser.parse_args(argv)
    _use_utf8(sys.stdout)

    try:
        root = Path.cwd()
        # 書き出す前に全件を組み立てる。1 件でも失敗したら、どのファイルも書き換えない
        try:
            plans = _plan(root)
        except BuildError as error:
            print(str(error), file=sys.stderr)
            return _EXIT_NOT_BUILT
        written = sorted(
            path for path, doc, items in plans if replace_items(root / path, doc, items)
        )
        for path in written:
            print(path)
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返す
        traceback.print_exc()
        return _EXIT_UNEXPECTED
    return 0


def _plan(root: Path) -> list[tuple[PurePosixPath, CommentedMap, list[dict[str, str]]]]:
    """種類のスキーマごとに、テンプレートのパス・文書・組み立てた items を返す。"""
    schemas = load_schemas(root)
    plans: list[tuple[PurePosixPath, CommentedMap, list[dict[str, str]]]] = []
    for name, schema in schemas.docs.items():
        template_id = TEMPLATE_IDS.get(cast("str", schema.get("x-kind")))
        # 対応表に行が無いスキーマ（共通・目次）は生成しない
        if template_id is None:
            continue
        path = TEMPLATES_DIR / f"{template_id}.yaml"
        try:
            doc = load_document((root / path).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, DocumentError) as error:
            raise BuildError(
                str(path), f"テンプレートがありません: {template_id}（{SCHEMAS_DIR / name}）"
            ) from error
        plans.append((path, doc, build_items(name, schemas)))
    return plans


def load_schemas(root: Path, *, check_refs: bool = True) -> SchemaSet:
    """schemas/design/ の全てのスキーマを読み、ファイル名を URI にして登録し、$ref を確かめる。"""
    folder = root / SCHEMAS_DIR
    if not folder.is_dir():
        raise BuildError(str(SCHEMAS_DIR), "スキーマを読めません: フォルダがありません")

    docs: dict[str, Mapping[str, object]] = {}
    for path in sorted(folder.glob("*.schema.yaml")):
        relative = str(SCHEMAS_DIR / path.name)
        try:
            data = load_safe(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, YAMLError) as error:
            raise BuildError(relative, f"スキーマを読めません: {error}") from error
        schema = as_mapping(data)
        if schema is None:
            raise BuildError(relative, "スキーマを読めません: 最上位がマッピングではありません")
        docs[path.name] = schema

    registry = Registry[Any]().with_resources(
        (name, cast("Resource[Any]", DRAFT202012.create_resource(doc)))
        for name, doc in docs.items()
    )
    if check_refs:
        for name, doc in docs.items():
            resolver = registry.resolver(base_uri=name)
            for ref in _iter_refs(doc):
                try:
                    resolver.lookup(ref)
                except Unresolvable as error:
                    raise BuildError(
                        str(SCHEMAS_DIR / name), f"$ref: {ref} を解決できません"
                    ) from error
    return SchemaSet(docs, registry)


def _iter_refs(node: object) -> Iterator[str]:
    """スキーマの全ての深さの $ref の値を返す。"""
    items = as_list(node)
    if items is not None:
        for value in items:
            yield from _iter_refs(value)
        return
    schema = as_mapping(node)
    if schema is None:
        return
    ref = schema.get("$ref")
    if isinstance(ref, str):
        yield ref
    for key, value in schema.items():
        # データの値（examples・enum など）の中はスキーマではない
        if key in _DATA_KEYWORDS:
            continue
        named = as_mapping(value) if key in _NAMED_SCHEMA_KEYWORDS else None
        # 名前 → スキーマの対応は、値のスキーマだけを辿る
        if named is not None:
            for child in named.values():
                yield from _iter_refs(child)
        else:
            yield from _iter_refs(value)


def build_items(name: str, schemas: SchemaSet) -> list[dict[str, str]]:
    """種類のスキーマ 1 件から、テンプレートの items を組み立てる。"""
    schema = schemas.docs[name]
    resolver = schemas.registry.resolver(base_uri=name)
    items: list[dict[str, str]] = []

    description = schema.get("description")
    if isinstance(description, str):
        items.append({"id": "overview", "name": "概要", "body": description.strip()})
    rules = _strings(schema.get("x-rules"))
    if rules:
        items.append(
            {"id": "rules-01", "name": "決まり", "body": "\n".join(f"- {rule}" for rule in rules)}
        )

    # キーの $ref が解決できないときは、どのスキーマのどの $ref かを返す
    try:
        rows = list(_iter_keys(schema, resolver))
    except Unresolvable as error:
        raise BuildError(
            str(SCHEMAS_DIR / name), f"$ref: {getattr(error, 'ref', error)} を解決できません"
        ) from error
    if rows:
        items.append({"id": "item-list-01", "name": "項目", "body": _render_key_table(rows)})
    key_rules = _render_key_rules(rows)
    if key_rules is not None:
        items.append({"id": "key-rules-01", "name": "キーごとの決まり", "body": key_rules})

    examples = as_list(schema.get("examples")) or []
    for number, example in enumerate(examples, start=1):
        # 記載例が 2 件以上のときだけ名前に番号を付ける
        title = "記載例" if len(examples) == 1 else f"記載例 {number}"
        items.append(
            {
                "id": f"example-sample-{number:02d}",
                "name": title,
                "body": f"```yaml\n{_dump_block(example)}```",
            }
        )
    return items


def _strings(value: object) -> list[str]:
    """文字列の配列なら文字列だけを返す。配列でなければ空。"""
    return [item for item in as_list(value) or [] if isinstance(item, str)]


def _resolve(
    schema: Mapping[str, object], resolver: Resolver[Any]
) -> tuple[Mapping[str, object], Resolver[Any]]:
    """$ref を辿った先に、キーの側の値を重ねたスキーマと、その先の解決器を返す。"""
    ref = schema.get("$ref")
    if not isinstance(ref, str):
        return schema, resolver
    resolved = resolver.lookup(ref)
    target = as_mapping(resolved.contents) or {}
    # 解決した先がさらに $ref を持てば、その先の解決器で続けて引く
    base, next_resolver = _resolve(target, resolved.resolver)
    merged = {**base, **{key: value for key, value in schema.items() if key != "$ref"}}
    return merged, next_resolver


def _iter_keys(
    schema: Mapping[str, object], resolver: Resolver[Any], prefix: str = ""
) -> Iterator[KeyRow]:
    """properties を深さ優先でスキーマの並びのとおりにたどり、$ref を解決したキーの行を返す。"""
    properties = as_mapping(schema.get("properties")) or {}
    required = set(_strings(schema.get("required")))
    for key, value in properties.items():
        sub = as_mapping(value)
        if sub is None:
            continue
        merged, sub_resolver = _resolve(sub, resolver)
        name = f"{prefix}{key}"
        yield KeyRow(name=name, schema=merged, required=key in required)
        # オブジェクトの子は parent.child でたどる
        if as_mapping(merged.get("properties")) is not None:
            yield from _iter_keys(merged, sub_resolver, f"{name}.")
        # 配列の要素の子は parent[].child でたどる
        element = as_mapping(merged.get("items"))
        if element is not None:
            element_schema, element_resolver = _resolve(element, sub_resolver)
            if as_mapping(element_schema.get("properties")) is not None:
                yield from _iter_keys(element_schema, element_resolver, f"{name}[].")


def _render_table(columns: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """列と行から、<!-- table: data --> で包んだ表の Markdown を作る。"""
    lines = [
        _TABLE_OPEN,
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
        *("| " + " | ".join(row) + " |" for row in rows),
        "",
        _TABLE_CLOSE,
    ]
    return "\n".join(lines)


def _type_of(schema: Mapping[str, object]) -> str | None:
    """型の列の値を返す。型が無ければ None。"""
    type_value = schema.get("type")
    if isinstance(type_value, str):
        return type_value
    types = _strings(type_value)
    if types:
        return " / ".join(types)
    # type が無く anyOf・oneOf だけを持つときは、各要素の type をつなぐ
    options = as_list(schema.get("anyOf")) or as_list(schema.get("oneOf")) or []
    option_types = [
        option_type
        for option in options
        if isinstance(option_type := (as_mapping(option) or {}).get("type"), str)
    ]
    return " / ".join(option_types) if option_types else None


def _code(value: object) -> str:
    """値を 1 行のインラインコードにする（値がバッククォートを含むときは 2 つで囲む）。"""
    text = _flow(value)
    if "`" in text:
        return f"`` {text} ``"
    return f"`{text}`"


def _join_code(values: object) -> str | None:
    """配列の要素ごとにインラインコードにして / でつなぐ。配列でないか空なら None。"""
    items = as_list(values)
    if not items:
        return None
    return " / ".join(_code(item) for item in items)


def _render_key_table(rows: Sequence[KeyRow]) -> str:
    """キーの行から、キーの表の Markdown を作る。"""
    body: list[list[str]] = []
    for row in rows:
        schema = row.schema
        constraints = ", ".join(
            f"{key}: {_code(schema[key])}" for key in CONSTRAINT_KEYS if key in schema
        )
        body.append(
            [
                _format_cell(row.name),
                _format_cell(schema.get("title")),
                _format_cell(_type_of(schema)),
                _format_cell("必須" if row.required else None),
                # 選択肢・制約・examples の値は Markdown として読ませないよう、文字列もインラインコードにする
                _format_cell(_join_code(schema.get("enum"))),
                _format_cell(constraints or None),
                _format_cell(schema.get("description")),
                _format_cell(_join_code(schema.get("examples"))),
            ]
        )
    return _render_table(_KEY_TABLE_COLUMNS, body)


def _render_key_rules(rows: Sequence[KeyRow]) -> str | None:
    """決まりか悪い例を持つキーの行から、キーごとの決まりの表の Markdown を作る。"""
    body: list[list[str]] = []
    for row in rows:
        rules = _strings(row.schema.get("x-rules"))
        bads = [bad for bad in as_list(row.schema.get("x-bad-examples")) or [] if as_mapping(bad)]
        # 決まりも悪い例も持たないキーは行に出さない
        if not rules and not bads:
            continue
        name = _format_cell(row.name)
        rule_cell = "<br>".join(_format_cell(rule) for rule in rules) if rules else "-"
        if not bads:
            body.append([name, rule_cell, "-", "-"])
            continue
        for index, bad in enumerate(bads):
            mapping = as_mapping(bad) or {}
            # 2 件目からは、名前と決まりのセルを空にする
            head = [name, rule_cell] if index == 0 else ["", ""]
            body.append(
                [
                    *head,
                    _format_cell(mapping.get("value")),
                    _format_cell(mapping.get("reason")),
                ]
            )
    if not body:
        return None
    return _render_table(_KEY_RULES_COLUMNS, body)


def _flow(value: object) -> str:
    """値を 1 行の YAML（フロースタイル）の文字列にする。文字列はそのまま返す。"""
    if isinstance(value, str):
        return value
    yaml = YAML(typ="safe", pure=True)
    yaml.default_flow_style = True
    yaml.width = 4096
    stream = io.StringIO()
    yaml.dump(value, stream)  # pyright: ignore[reportUnknownMemberType]
    text = stream.getvalue()
    # スカラーは文書の終わりの「...」が付くので外す
    text = text.removesuffix("...\n")
    return text.strip()


def _inline(value: object) -> str:
    """文字列はそのまま、文字列でない値はバッククォートで囲んだ 1 行の YAML にする。"""
    if isinstance(value, str):
        return value
    return f"`{_flow(value)}`"


def _format_cell(value: object) -> str:
    """表のセル 1 つの値を、表の中に置ける 1 行の文字列にする。"""
    if value is None:
        return "-"
    text = _inline(value)
    return text.replace("\n", "<br>").replace("|", "\\|")


def _literal(value: object) -> object:
    """複数行の文字列をブロックスカラーにして、記載例の YAML で読みやすくする。"""
    items = as_list(value)
    if items is not None:
        return [_literal(item) for item in items]
    mapping = as_mapping(value)
    if mapping is not None:
        return {key: _literal(item) for key, item in mapping.items()}
    if isinstance(value, str) and "\n" in value:
        return LiteralScalarString(value)
    return value


def _dump_block(value: object) -> str:
    """記載例の値をブロックスタイルの YAML にする（末尾に改行を 1 つ付ける）。"""
    yaml = YAML(typ="rt")
    yaml.width = 4096
    stream = io.StringIO()
    yaml.dump(_literal(value), stream)  # pyright: ignore[reportUnknownMemberType]
    return stream.getvalue()


def read_items(doc: CommentedMap) -> list[dict[str, str]]:
    """テンプレートの文書の items を id・name・body の組の並びにする。"""
    items: list[dict[str, str]] = []
    for item in as_list(cast("Mapping[str, object]", doc).get("items")) or []:
        mapping = as_mapping(item) or {}
        items.append({key: str(mapping.get(key, "")) for key in ("id", "name", "body")})
    return items


def replace_items(path: Path, doc: CommentedMap, items: Sequence[Mapping[str, str]]) -> bool:
    """テンプレートの文書の items が組み立てた items と違えば置き換えて書き出す。"""
    if read_items(doc) == [dict(item) for item in items]:
        return False
    # 引用符・コメント・キーの並びを残すため、引用符を保つ往復の読み書きで読み直す
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    data = cast("CommentedMap", yaml.load(path.read_text(encoding="utf-8")))  # pyright: ignore[reportUnknownMemberType]
    data["items"] = CommentedSeq(
        CommentedMap(
            [
                ("id", item["id"]),
                ("name", item["name"]),
                ("body", LiteralScalarString(item["body"])),
            ]
        )
        for item in items
    )
    stream = io.StringIO()
    yaml.dump(data, stream)  # pyright: ignore[reportUnknownMemberType]
    path.write_text(stream.getvalue(), encoding="utf-8", newline="\n")
    return True


if __name__ == "__main__":
    sys.exit(main())
