"""開発者がスキーマから設計書のテンプレートを生成する（SC-201-1）の E2E テスト。"""

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from ruamel.yaml import YAML

# conftest の fixture の型。子プロセスの結果は subprocess.CompletedProcess
type KnowledgeClone = Callable[..., Path]
type RunCheckAll = Callable[..., Any]

# リポジトリの直下
_REPO = Path(__file__).resolve().parents[3]
# 生成のコマンドを待つ秒数（uv の依存の取得を含む）
_WAIT_SEC = 120
# 生成のコマンド
_COMMAND = ("uv", "run", "--frozen", "--script", "scripts/build_templates.py")
# ER 図のスキーマと、そのテンプレート
_ER_SCHEMA = "schemas/design/er.schema.yaml"
_ER_TEMPLATE = "docs/template/template-er.yaml"
# ER 図のスキーマの id のキーの x-rules の行と、その後ろに追加する決まり
_ID_RULE = "      - 設計書を作るときに振り、改名・移動でも変えない。\n"
_ADDED_RULE = "e2e で追加した決まり。"
# 生成の対象の設計書の種類のテンプレート
_TEMPLATES = (
    "template-architecture",
    "template-component",
    "template-config",
    "template-dataflow",
    "template-dev-command",
    "template-er",
    "template-external-api",
    "template-external-library",
    "template-interface",
    "template-layout",
    "template-module",
    "template-nonfunctional",
    "template-scenario",
    "template-screen-design",
    "template-state-transition",
    "template-test-procedure",
)
# items の外のキー
_METADATA_KEYS = ("id", "name", "description", "tags", "status", "visibility", "rev")


def _run_build(folder: Path) -> subprocess.CompletedProcess[str]:
    """生成のコマンドを、クローンの直下で子プロセスとして起動する。"""
    return subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
        _COMMAND,
        cwd=folder,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=_WAIT_SEC,
    )


def _bytes_of_templates(folder: Path) -> dict[str, bytes]:
    """生成の対象の全てのテンプレートのバイト列を返す。"""
    return {
        name: (folder / "docs" / "template" / f"{name}.yaml").read_bytes() for name in _TEMPLATES
    }


def _load(path: Path) -> dict[str, Any]:
    """YAML を読む。"""
    return cast("dict[str, Any]", YAML(typ="safe").load(path.read_text(encoding="utf-8")))  # pyright: ignore[reportUnknownMemberType]


def test_normal(knowledge_clone: KnowledgeClone, run_check_all: RunCheckAll) -> None:
    """スキーマに決まりを 1 件追加して生成のコマンドを実行すると、そのテンプレートだけが書き換わる（正常シナリオ）。"""
    # 準備
    schema = (_REPO / _ER_SCHEMA).read_text(encoding="utf-8")
    clone = knowledge_clone(
        {_ER_SCHEMA: schema.replace(_ID_RULE, f"{_ID_RULE}      - {_ADDED_RULE}\n", 1)}
    )
    before = _bytes_of_templates(clone)
    metadata_before = _load(clone / _ER_TEMPLATE)
    # 実行
    result = _run_build(clone)
    # 検証
    assert result.returncode == 0
    assert result.stdout == f"{_ER_TEMPLATE}\n"
    after = _bytes_of_templates(clone)
    assert {name for name in _TEMPLATES if after[name] != before[name]} == {"template-er"}
    doc = _load(clone / _ER_TEMPLATE)
    rules = next(item["body"] for item in doc["items"] if item["id"] == "key-rules-01")
    assert _ADDED_RULE in rules
    assert {key: doc.get(key) for key in _METADATA_KEYS} == {
        key: metadata_before.get(key) for key in _METADATA_KEYS
    }
    checked = run_check_all(clone)
    assert checked.returncode == 0


def test_error_when_schema_unresolvable(knowledge_clone: KnowledgeClone) -> None:
    """スキーマの $ref を解決できなければ、どのファイルも書き換えずに終了コード 2 で終わる（異常シナリオ）。"""
    # 準備
    schema = (_REPO / _ER_SCHEMA).read_text(encoding="utf-8")
    clone = knowledge_clone(
        {
            _ER_SCHEMA: schema.replace(
                "$ref: common.schema.yaml#/$defs/id",
                "$ref: common.schema.yaml#/$defs/e2e-missing",
                1,
            )
        }
    )
    before = _bytes_of_templates(clone)
    # 実行
    result = _run_build(clone)
    # 検証
    assert result.returncode == 2
    assert _ER_SCHEMA in result.stderr
    assert "common.schema.yaml#/$defs/e2e-missing" in result.stderr
    assert _bytes_of_templates(clone) == before


def test_error_when_template_missing(
    knowledge_clone: KnowledgeClone, git: Callable[..., str]
) -> None:
    """対応するテンプレートが無ければ、どのファイルも書き換えずに終了コード 2 で終わる（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    git(clone, "rm", "--quiet", _ER_TEMPLATE)
    rest = {name for name in _TEMPLATES if name != "template-er"}
    before = {name: (clone / "docs" / "template" / f"{name}.yaml").read_bytes() for name in rest}
    # 実行
    result = _run_build(clone)
    # 検証
    assert result.returncode == 2
    assert "template-er" in result.stderr
    assert _ER_SCHEMA in result.stderr
    assert {
        name: (clone / "docs" / "template" / f"{name}.yaml").read_bytes() for name in rest
    } == before
