# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "jsonschema>=4.26.0",
#     "ruamel.yaml==0.19.1",
# ]
# ///
"""dev-docs.yaml の documents[] が指す全ての文書にスキーマの検査と文書の違反の検査を当て、終了コードで合否を返す。

CI と手元から、リポジトリの直下で起動する。違反は 1 件 1 行で「{ファイルのパス}:{行}: {項目のパス}: {内容}」と出す。

Usage:
# 全ての文書を検査する（違反があれば終了コード 1）
uv run --frozen --script scripts/check_all.py
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

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from ruamel.yaml.error import YAMLError

from _common import (
    LIMIT_SEC,
    ConfigError,
    DocumentError,
    as_list,
    as_mapping,
    format_path,
    line_of,
    list_row_files,
    load_config,
    load_document,
    load_safe,
    read_texts,
)
from _maid import find_maid
from knowledge_checks import build_id_index, check_document

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

# validators[] の文書の違反の検査の id
CHECKS_ID = "knowledge-checks"

# 互いに $ref で引き合うスキーマの置き場所と名前
_SCHEMAS_GLOB = "schemas/*.schema.yaml"

# 文書の違反の検査の rule の先頭の「{行} 行目: 」
_RULE_LINE = re.compile(r"^(\d+) 行目: (.*)$", re.DOTALL)

# maid が PATH に無いときに標準エラーへ出す理由
_MAID_MISSING = (
    "maid が PATH にありません。開発コマンドの『環境構築（クローン直後）』で maid を入れてください"
)

# 終了コード。1 = 違反がある・想定していない例外、2 = 検査を始めなかった
_EXIT_VIOLATIONS = 1
_EXIT_NOT_STARTED = 2


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
    parser.parse_args(argv)
    _use_utf8(sys.stdout)

    try:
        # maid が無ければ検査を始めない
        executable = find_maid()
        if executable is None:
            print(_MAID_MISSING, file=sys.stderr)
            return _EXIT_NOT_STARTED
        root = Path.cwd()
        try:
            rows = load_config(root)
        except ConfigError as error:
            print(error.message, file=sys.stderr)
            return _EXIT_NOT_STARTED

        targets = list_targets(root, rows)
        texts = read_texts([root / target.path for target in targets])
        validators = build_validators(root, dict.fromkeys(target.schema for target in targets))
        # ID の索引は全ての文書で 1 度だけ作る
        index = build_id_index(root)

        count = 0
        for target in targets:
            text = texts[root / target.path]
            for line, path, message in check_target(
                target, text, validators[target.schema], root, executable, index
            ):
                print(f"{target.path}:{line}: {path}: {message}")
                count += 1
        print(f"{len(targets)} 件の文書を検査し、違反は {count} 件でした")
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返す
        traceback.print_exc()
        return _EXIT_VIOLATIONS
    else:
        return _EXIT_VIOLATIONS if count else 0


def _strings(value: object) -> list[str]:
    """文字列の配列の値から文字列だけを返す。配列でなければ空。"""
    elements = as_list(value)
    if elements is None:
        return []
    return [element for element in elements if isinstance(element, str)]


def list_targets(root: Path, rows: Sequence[Mapping[str, Any]]) -> list[Target]:
    """documents[] の行の paths・exclude に当たるファイルを、当てる検査と並べて返す。"""
    # 同じファイルは最初に当たった行で 1 件にする
    targets: dict[PurePosixPath, Target] = {}
    for row in rows:
        schema = row.get("schema")
        # 無効な行と、スキーマを持たない行は検査しない
        if row.get("enabled") is False or not isinstance(schema, str) or not schema:
            continue
        checks = CHECKS_ID in _strings(row.get("validators"))
        for relative in list_row_files(root, row):
            targets.setdefault(relative, Target(path=relative, schema=schema, checks=checks))
    return sorted(targets.values(), key=lambda target: target.path)


def build_validators(
    root: Path, schema_paths: Iterable[str]
) -> dict[str, Draft202012Validator | str]:
    """schemas/*.schema.yaml を互いの $ref で引けるようにした、スキーマのパス → 検査器を作る。"""
    # ファイル名を URI にして登録する（common.schema.yaml#/$defs/... の $ref を解く）
    resources: list[tuple[str, Resource[Any]]] = []
    for path in sorted(root.glob(_SCHEMAS_GLOB)):
        try:
            contents = as_mapping(load_safe(path.read_text(encoding="utf-8")))
        except OSError, UnicodeDecodeError, YAMLError:
            # 読めないスキーマは、それを使う行の検査器を作るときに理由を返す
            continue
        if contents is not None:
            resources.append(
                (path.name, cast("Resource[Any]", DRAFT202012.create_resource(contents)))
            )
    registry = Registry[Any]().with_resources(resources)

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
        validators[schema_path] = Draft202012Validator(schema, registry=registry)
    return validators


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
        for violation in check_document(text, root, executable, deadline, index=index):
            line, rule = _split_line(violation["rule"])
            results.append((line, violation["path"], rule))
    return results


if __name__ == "__main__":
    sys.exit(main())
