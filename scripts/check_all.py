# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "jsonschema>=4.26.0",
#     "ruamel.yaml==0.19.1",
#     "yamllint==1.38.0",
# ]
# ///
"""dev-docs.yaml の documents[] が指す全ての文書にスキーマの検査と文書の違反の検査を当て、終了コードで合否を返す。

手元から、リポジトリの直下で起動する。違反は 1 件 1 行で「{ファイルのパス}:{行}: {項目のパス}: {内容}」と出す。
対応表のコピーが正本と一致するか、設計書のテンプレートがスキーマと一致するかも確かめ、文書に markdownlint-cli2・textlint・yamllint を当てる。

Usage:
# 全ての文書を検査する（違反があれば終了コード 1）
uv run --frozen --script scripts/check_all.py
# lint の設定と npm の依存を別のフォルダから使う
uv run --frozen --script scripts/check_all.py [--lint-dir {フォルダ}]
"""

import argparse
import io
import re
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

from build_templates import (
    COMMAND,
    SCHEMAS_DIR,
    TEMPLATE_IDS,
    TEMPLATES_DIR,
    BuildError,
    build_items,
    load_schemas,
    read_items,
)
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012
from ruamel.yaml.error import YAMLError

from _common import (
    LIMIT_SEC,
    ConfigError,
    DocumentError,
    as_mapping,
    format_path,
    key_line,
    line_of,
    list_row_files,
    load_config,
    load_document,
    load_safe,
    read_texts,
    strings,
)
from _lint import (
    DEFAULT_LINT_DIR,
    YAMLLINT_SCHEMAS_CONFIG,
    LintFinding,
    LintOutputError,
    LintSource,
    collect_sources,
    find_lint_clis,
    load_yamllint_config,
    run_markdown_lints,
    run_yamllint,
)
from _maid import find_maid
from build_word_list import COPY, SOURCE, render_copy
from knowledge_checks import build_id_index, build_name_index, check_document

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping, Sequence

    from ruamel.yaml.comments import CommentedMap

    from _common import PathPart

# validators[] の文書の違反の検査の id
CHECKS_ID = "knowledge-checks"

# documents[] に無く、yamllint を当てるリポジトリの直下のファイル
YAMLLINT_EXTRA = ("dev-docs.yaml", "rules.yaml")

# 設計書のスキーマ（knowledge の正本）を置くフォルダ
DESIGN_SCHEMAS_DIR = PurePosixPath("schemas/design")

# JSON Schema 2020-12 のメタスキーマに x-rules・x-bad-examples の形を足したメタスキーマ
META_SCHEMA_PATH = PurePosixPath("schemas/meta.schema.yaml")

# スキーマのキーワードのうち、値がスキーマではなくデータのもの
_DATA_KEYWORDS = frozenset({"examples", "enum", "const", "default", "x-bad-examples"})

# スキーマのキーワードのうち、値が名前 → スキーマの対応のもの
_NAMED_SCHEMA_KEYWORDS = frozenset({"properties", "patternProperties", "$defs", "dependentSchemas"})

# yamllint を当てる文書の拡張子
_YAML_SUFFIXES = (".yaml", ".yml")

# 互いに $ref で引き合うスキーマの置き場所と名前
_SCHEMAS_GLOB = "schemas/*.schema.yaml"

# 文書の違反の検査の rule の先頭の「{行} 行目: 」
_RULE_LINE = re.compile(r"^(\d+) 行目: (.*)$", re.DOTALL)

# 検査の CLI が引けないときに標準エラーへ出す理由
_CLI_MISSING = "{name} がありません。開発コマンドの『環境構築（クローン直後）』で入れてください"

# 終了コード。1 = 違反がある・想定していない例外、2 = 検査を始めなかった
_EXIT_VIOLATIONS = 1
_EXIT_NOT_STARTED = 2


class MetaSchemaError(Exception):
    """schemas/meta.schema.yaml が無い・読めない・メタスキーマに合わない。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        # 標準エラーへ出す理由の 1 行
        self.message = message


@dataclass(frozen=True)
class Target:
    """documents[] の行から引いた文書 1 件と、当てる検査。"""

    # リポジトリの直下からのパス
    path: PurePosixPath
    # 行の schema（schemas/rule.schema.yaml など）
    schema: str
    # 行の validators に knowledge-checks を持つか
    checks: bool


def _use_utf8(stream: object) -> None:
    """標準出力を UTF-8 にする（Windows の既定のエンコーディングで書かない）。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """全ての文書を検査し、違反を 1 件 1 行で出して終了コードで合否を返す。"""
    parser = argparse.ArgumentParser(description="dev-docs.yaml が指す全ての文書の違反を出す")
    parser.add_argument(
        "--lint-dir",
        type=Path,
        default=DEFAULT_LINT_DIR,
        help="lint の設定と npm の依存（node_modules/.bin/）を持つフォルダ",
    )
    args = parser.parse_args(argv)
    lint_dir = cast("Path", args.lint_dir)
    _use_utf8(sys.stdout)

    try:
        # 検査の CLI が 1 つでも無ければ検査を始めない
        executable = find_maid()
        lint_clis = find_lint_clis(lint_dir)
        missing = [
            name for name, found in {"maid": executable, **lint_clis}.items() if found is None
        ]
        if executable is None or missing:
            for name in missing:
                print(_CLI_MISSING.format(name=name), file=sys.stderr)
            return _EXIT_NOT_STARTED
        clis = {name: path for name, path in lint_clis.items() if path is not None}
        root = Path.cwd()
        # dev-docs.yaml か拡張したメタスキーマを使えなければ検査を始めない
        try:
            rows = load_config(root)
            meta = load_meta_validator(root)
        except (ConfigError, MetaSchemaError) as error:
            print(error.message, file=sys.stderr)
            return _EXIT_NOT_STARTED

        targets = list_targets(root, rows)
        texts = read_texts([root / target.path for target in targets])
        validators = build_validators(root, dict.fromkeys(target.schema for target in targets))
        # ID の索引と名前の索引は全ての文書で 1 度だけ作る
        index = build_id_index(root)
        names = build_name_index(root, rows)

        count = 0
        for target in targets:
            text = texts[root / target.path]
            for line, path, message in check_target(
                target, text, validators[target.schema], root, executable, index, names
            ):
                print(f"{target.path}:{line}: {path}: {message}")
                count += 1
        # スキーマが自身の検査を通るかと、対応表のコピーと設計書のテンプレートが正本と一致するか
        for file_path, line, path, message in (
            *check_design_schemas(root, meta),
            *check_document_schemas(root, meta),
            *check_word_list_copy(root),
            *check_design_templates(root),
        ):
            print(f"{file_path}:{line}: {path}: {message}")
            count += 1
        # lint の違反は失敗させるルールだけを数え、警告にしたルールは警告として数える
        try:
            findings = check_lints(root, targets, texts, lint_dir, clis)
        except LintOutputError as error:
            print(error.message, file=sys.stderr)
            return _EXIT_VIOLATIONS
        warnings = _print_lints(findings)
        count += len(findings) - warnings
        print(f"{len(targets)} 件の文書を検査し、違反は {count} 件、警告は {warnings} 件でした")
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返す
        traceback.print_exc()
        return _EXIT_VIOLATIONS
    else:
        return _EXIT_VIOLATIONS if count else 0


def _print_lints(findings: Sequence[LintFinding]) -> int:
    """lint の違反を 1 件 1 行で出し、警告にしたルールの違反の数を返す。"""
    warnings = 0
    for finding in findings:
        prefix = "warning: " if finding.warning else ""
        print(
            f"{finding.path}:{finding.line}: {finding.item_path}: "
            f"{prefix}{finding.tool}/{finding.rule}: {finding.message}"
        )
        if finding.warning:
            warnings += 1
    return warnings


def list_targets(root: Path, rows: Sequence[Mapping[str, Any]]) -> list[Target]:
    """documents[] の行の paths・exclude に当たるファイルを、当てる検査と並べて返す。"""
    # 同じファイルは最初に当たった行で 1 件にする
    targets: dict[PurePosixPath, Target] = {}
    for row in rows:
        schema = row.get("schema")
        # 無効な行と、スキーマを持たない行は検査しない
        if row.get("enabled") is False or not isinstance(schema, str) or not schema:
            continue
        checks = CHECKS_ID in strings(row.get("validators"))
        for relative in list_row_files(root, row):
            targets.setdefault(relative, Target(path=relative, schema=schema, checks=checks))
    return sorted(targets.values(), key=lambda target: target.path)


def build_validators(
    root: Path, schema_paths: Iterable[str]
) -> dict[str, Draft202012Validator | str]:
    """行の schema と同じフォルダのスキーマを互いの $ref で引けるようにした、パス → 検査器を作る。"""
    # フォルダごとに別の登録にし、schemas/ の knowledge-common.schema.yaml#/$defs/... と、
    # schemas/design/ の common.schema.yaml#/$defs/... の $ref を取り違えずに解く
    registries: dict[PurePosixPath, Registry[Any]] = {}
    validators: dict[str, Draft202012Validator | str] = {}
    for schema_path in schema_paths:
        try:
            schema = cast(
                "Mapping[str, Any]", load_safe((root / schema_path).read_text(encoding="utf-8"))
            )
            Draft202012Validator.check_schema(schema)
        except (OSError, UnicodeDecodeError, YAMLError) as error:
            validators[schema_path] = f"読めません: {error}"
            continue
        except SchemaError as error:
            validators[schema_path] = f"スキーマとして正しくありません: {error.message}"
            continue
        folder = PurePosixPath(schema_path).parent
        if folder not in registries:
            registries[folder] = _folder_registry(root / folder)
        validators[schema_path] = Draft202012Validator(schema, registry=registries[folder])
    return validators


def _folder_registry(folder: Path) -> Registry[Any]:
    """フォルダの *.schema.yaml を、ファイル名を URI にして登録した Registry を返す。"""
    resources: list[tuple[str, Resource[Any]]] = []
    for path in sorted(folder.glob("*.schema.yaml")):
        try:
            contents = as_mapping(load_safe(path.read_text(encoding="utf-8")))
        except OSError, UnicodeDecodeError, YAMLError:
            # 読めないスキーマは、それを使う行の検査器を作るときに理由を返す
            continue
        if contents is not None:
            resources.append(
                (path.name, cast("Resource[Any]", DRAFT202012.create_resource(contents)))
            )
    return Registry[Any]().with_resources(resources)


def _split_line(rule: str) -> tuple[int, str]:
    """違反の rule の先頭の「{行} 行目: 」を行と残りに分ける。"""
    matched = _RULE_LINE.match(rule)
    if matched is None:
        return 1, rule
    return int(matched.group(1)), matched.group(2)


def check_target(
    target: Target,
    text: str | None,
    validator: Draft202012Validator | str,
    root: Path,
    executable: str,
    index: Mapping[str, frozenset[str]],
    names: Mapping[str, Sequence[tuple[str, str]]],
) -> list[tuple[int, str, str]]:
    """文書 1 件にスキーマの検査と文書の違反の検査を当て、（行、項目のパス、内容）で返す。"""
    if text is None:
        return [(1, "$", "ファイルを UTF-8 で読めません")]
    try:
        doc = load_document(text)
    except DocumentError as error:
        return [(error.line, "$", f"YAML として読めません: {error.message}")]

    results: list[tuple[int, str, str]] = []
    # 検査器を作れなかったスキーマ: 理由を 1 件にする
    if isinstance(validator, str):
        results.append((1, "$", f"スキーマ {target.schema} を使えません: {validator}"))
    else:
        errors = cast("Iterable[ValidationError]", validator.iter_errors(doc))  # pyright: ignore[reportUnknownMemberType]
        for error in errors:
            parts = list(error.absolute_path)
            results.append((line_of(doc, parts), format_path(parts), f"schema: {error.message}"))

    # 文書の違反の検査は、validators に knowledge-checks を持つ行の文書だけに当てる
    if target.checks:
        deadline = time.monotonic() + LIMIT_SEC
        for violation in check_document(text, root, executable, deadline, index=index, names=names):
            line, rule = _split_line(violation["rule"])
            results.append((line, violation["path"], rule))
    return results


def check_lints(
    root: Path,
    targets: Sequence[Target],
    texts: Mapping[Path, str | None],
    lint_dir: Path,
    clis: Mapping[str, str],
) -> list[LintFinding]:
    """設計書を含む文書の Markdown に markdownlint-cli2・textlint、YAML のファイルに yamllint を当てる。"""
    sources: list[LintSource] = []
    yaml_files: list[tuple[PurePosixPath, str]] = []
    for target in targets:
        text = texts.get(root / target.path)
        # 読めなかった文書の違反は文書 1 件の検査が出す
        if text is None:
            continue
        sources.extend(collect_sources(target.path, text))
        if target.path.suffix in _YAML_SUFFIXES:
            yaml_files.append((target.path, text))
    # documents[] に無い直下の設定ファイルは、在るものだけに当てる
    for name in YAMLLINT_EXTRA:
        path = root / name
        if path.is_file():
            yaml_files.append((PurePosixPath(name), path.read_text(encoding="utf-8")))

    findings = run_markdown_lints(sources, lint_dir, clis)
    config = load_yamllint_config(lint_dir)
    for path, text in yaml_files:
        findings.extend(run_yamllint(path, text, config))
    # schemas/ のスキーマには、フロー形式を違反にする設定だけを当てる
    schemas_config = load_yamllint_config(lint_dir, YAMLLINT_SCHEMAS_CONFIG)
    for path, text in _read_schema_texts(root):
        findings.extend(run_yamllint(path, text, schemas_config))
    return sorted(findings, key=lambda finding: (str(finding.path), finding.line))


def _read_schema_texts(root: Path) -> list[tuple[PurePosixPath, str]]:
    """schemas/ の直下と schemas/design/ のスキーマを、パスの順に読む。"""
    paths = sorted([*root.glob(_SCHEMAS_GLOB), *(root / DESIGN_SCHEMAS_DIR).glob("*.schema.yaml")])
    texts: list[tuple[PurePosixPath, str]] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            # 読めないスキーマの違反は、設計書のスキーマの検査と文書の種類のスキーマの検査が出す
            continue
        texts.append((PurePosixPath(path.relative_to(root).as_posix()), text))
    return texts


def load_meta_validator(root: Path) -> Draft202012Validator:
    """schemas/meta.schema.yaml を読み、スキーマの検査器を作る。"""
    try:
        schema = load_safe((root / META_SCHEMA_PATH).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cast("Mapping[str, Any]", schema))
    except (OSError, UnicodeDecodeError, YAMLError) as error:
        message = f"{META_SCHEMA_PATH} を使えません: {error}"
        raise MetaSchemaError(message) from error
    except SchemaError as error:
        message = f"{META_SCHEMA_PATH} を使えません: {error.message}"
        raise MetaSchemaError(message) from error
    return Draft202012Validator(cast("Mapping[str, Any]", schema))


def check_document_schemas(
    root: Path, meta: Draft202012Validator
) -> list[tuple[str, int, str, str]]:
    """schemas/*.schema.yaml に、拡張したメタスキーマの検査を当てる。"""
    docs, results = _read_schemas(root, PurePosixPath("schemas"))
    for name, doc in docs.items():
        relative = str(PurePosixPath("schemas") / name)
        results.extend(
            (relative, line, path, message) for line, path, message in _check_meta(doc, meta)
        )
    return sorted(results, key=lambda result: (result[0], result[1]))


def _read_schemas(
    root: Path, folder: PurePosixPath
) -> tuple[dict[str, CommentedMap], list[tuple[str, int, str, str]]]:
    """フォルダの *.schema.yaml を読み、読めたスキーマと読めなかったファイルの違反を返す。"""
    results: list[tuple[str, int, str, str]] = []
    docs: dict[str, CommentedMap] = {}
    for path in sorted((root / folder).glob("*.schema.yaml")):
        relative = str(folder / path.name)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            results.append((relative, 1, "$", "ファイルを UTF-8 で読めません"))
            continue
        try:
            docs[path.name] = load_document(text)
        except DocumentError as error:
            results.append((relative, error.line, "$", f"YAML として読めません: {error.message}"))
    return docs, results


def _check_meta(doc: CommentedMap, meta: Draft202012Validator) -> list[tuple[int, str, str]]:
    """スキーマ 1 件のメタスキーマの違反を、行・項目のパス・内容の組で返す。"""
    errors = cast("list[ValidationError]", list(meta.iter_errors(doc)))  # pyright: ignore[reportUnknownMemberType]
    results: list[tuple[int, str, str]] = []
    for error in errors:
        parts = list(error.absolute_path)
        results.append((line_of(doc, parts), format_path(parts), f"metaschema: {error.message}"))
    return results


def check_design_schemas(root: Path, meta: Draft202012Validator) -> list[tuple[str, int, str, str]]:
    """schemas/design/ の設計書のスキーマに、拡張したメタスキーマ・$ref・examples の検査を当てる。"""
    # フォルダが無いリポジトリは検査しない
    if not (root / DESIGN_SCHEMAS_DIR).is_dir():
        return []

    docs, results = _read_schemas(root, DESIGN_SCHEMAS_DIR)

    # schemas/*.schema.yaml とは別に、ファイル名を URI にして登録する（同じ名前の common.schema.yaml を取り違えない）
    registry = Registry[Any]().with_resources(
        (name, cast("Resource[Any]", DRAFT202012.create_resource(doc)))
        for name, doc in docs.items()
    )
    for name, doc in docs.items():
        relative = str(DESIGN_SCHEMAS_DIR / name)
        meta_results = _check_meta(doc, meta)
        results.extend((relative, line, path, message) for line, path, message in meta_results)
        # メタスキーマに合わないスキーマは、$ref・examples を辿れないので後の検査を当てない
        if meta_results:
            continue
        for line, path, message in _check_schema_refs(name, doc, registry):
            results.append((relative, line, path, message))
    return sorted(results, key=lambda result: (result[0], result[1]))


def _iter_schemas(
    node: object, parts: tuple[PathPart, ...] = ()
) -> Iterator[tuple[tuple[PathPart, ...], Mapping[str, object]]]:
    """スキーマを辿り、スキーマのマッピングごとに（項目のパス、マッピング）を返す。"""
    if isinstance(node, list):
        for index, value in enumerate(cast("list[object]", node)):
            yield from _iter_schemas(value, (*parts, index))
        return
    schema = as_mapping(node)
    if schema is None:
        return
    yield parts, schema
    for key, value in schema.items():
        # データの値（examples・enum・const・default）の中はスキーマではない
        if key in _DATA_KEYWORDS:
            continue
        named = as_mapping(value) if key in _NAMED_SCHEMA_KEYWORDS else None
        # 名前 → スキーマの対応: キーは名前なので、キーワードと見なさずに値のスキーマを辿る
        if named is not None:
            for child_name, child in named.items():
                yield from _iter_schemas(child, (*parts, key, child_name))
        else:
            yield from _iter_schemas(value, (*parts, key))


def _json_pointer(parts: Sequence[PathPart]) -> str:
    """項目のパスを JSON Pointer にする。"""
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def _check_schema_refs(
    name: str, doc: CommentedMap, registry: Registry[Any]
) -> Iterator[tuple[int, str, str]]:
    """スキーマ 1 件の $ref の解決と examples の検査の誤りを（行、項目のパス、内容）で返す。"""
    resolver = registry.resolver(base_uri=name)
    for parts, schema in _iter_schemas(doc):
        ref = schema.get("$ref")
        # $ref: ファイル名を基準の URI にして登録から引く
        if isinstance(ref, str):
            try:
                resolver.lookup(ref)
            except Unresolvable:
                ref_parts = [*parts, "$ref"]
                yield (
                    line_of(doc, ref_parts),
                    format_path(ref_parts),
                    f"$ref: {ref} を解決できません",
                )
        examples = schema.get("examples")
        # examples: その examples を持つスキーマを $ref で指した検査器で、要素ごとに検査する
        if not isinstance(examples, list):
            continue
        validator = Draft202012Validator(
            {"$ref": f"{name}#{_json_pointer(parts)}"}, registry=registry
        )
        for index, example in enumerate(cast("list[object]", examples)):
            try:
                found = validator.iter_errors(cast("Any", example))  # pyright: ignore[reportUnknownMemberType]
                errors = cast("list[ValidationError]", list(found))
            except Unresolvable:
                # 解決できない $ref は $ref の検査が出す
                continue
            for error in errors:
                error_parts = [*parts, "examples", index, *error.absolute_path]
                yield (
                    line_of(doc, error_parts),
                    format_path(error_parts),
                    f"examples: {error.message}",
                )


def check_word_list_copy(root: Path) -> list[tuple[str, int, str, str]]:
    """正本から作り直したコピーの中身が、置いてあるコピーと一致するかを確かめる。"""
    # 正本が無い・読めないときの違反は文書の検査で出る
    try:
        doc = load_document((root / SOURCE).read_text(encoding="utf-8"))
    except OSError, UnicodeDecodeError, DocumentError:
        return []
    try:
        current = (root / COPY).read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        current = None
    if current == render_copy(doc):
        return []
    return [
        (
            str(COPY),
            1,
            "$",
            "対応表のコピーが正本と一致しません。uv run --frozen --script scripts/build_word_list.py で作り直してください",
        )
    ]


def check_design_templates(root: Path) -> list[tuple[str, int, str, str]]:
    """種類のスキーマから組み立てた items が、対応するテンプレートの items と一致するかを確かめる。"""
    if not (root / SCHEMAS_DIR).is_dir():
        return []
    # 読めないスキーマ・解決できない $ref は設計書のスキーマの検査が違反にする
    try:
        schemas = load_schemas(root, check_refs=False)
    except BuildError:
        return []

    results: list[tuple[str, int, str, str]] = []
    for name, schema in schemas.docs.items():
        template_id = TEMPLATE_IDS.get(cast("str", schema.get("x-kind")))
        # 対応表に行が無いスキーマ（共通・目次）はテンプレートを持たない
        if template_id is None:
            continue
        path = TEMPLATES_DIR / f"{template_id}.yaml"
        schema_path = SCHEMAS_DIR / name
        try:
            doc = load_document((root / path).read_text(encoding="utf-8"))
        except OSError, UnicodeDecodeError, DocumentError:
            results.append((str(path), 1, "$", f"テンプレートがありません: {schema_path}"))
            continue
        try:
            items = build_items(name, schemas)
        except BuildError:
            continue
        if read_items(doc) == items:
            continue
        line = key_line(doc, "items") if "items" in doc else 1
        results.append(
            (
                str(path),
                line,
                "items",
                f"テンプレートがスキーマ {schema_path} と一致しません。{COMMAND} で作り直してください",
            )
        )
    return sorted(results, key=lambda result: result[0])


if __name__ == "__main__":
    sys.exit(main())
