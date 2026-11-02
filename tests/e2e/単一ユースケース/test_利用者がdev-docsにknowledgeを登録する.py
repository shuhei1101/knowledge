"""利用者が dev-docs に knowledge を登録する（SC-72-2）の E2E テスト。"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。起動した dev-docs は conftest の Served
type KnowledgeClone = Callable[..., Path]
type Serve = Callable[..., Any]
type KnowledgeRow = Callable[..., Any]
type Register = Callable[..., Any]

# リポジトリの直下の dev-docs.yaml
_CONFIG = Path(__file__).resolve().parents[3] / "dev-docs.yaml"
# documents の先頭の行のスキーマを、存在しないファイルへ向ける置き換え
_BROKEN_SCHEMA = ("schema: schemas/rule.schema.yaml", "schema: schemas/missing.schema.yaml")


def test_normal(
    knowledge_clone: KnowledgeClone, serve: Serve, knowledge_row: KnowledgeRow, register: Register
) -> None:
    """点検を通した knowledge を `sources[]` に登録し、配信中になる（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    served = serve([])
    # 実行
    result = register(served, clone, knowledge_row(clone))
    # 検証
    sources = served.sources()
    status = {item["id"]: item for item in result.status.data["sources"]}
    assert not result.check.is_error
    assert "violations" not in result.check.data
    assert [source["id"] for source in sources] == ["knowledge"]
    assert sources[0]["config"] == [str(clone / "dev-docs.yaml")]
    assert sources[0]["scope"]["read"] == ["/**"]
    assert sources[0]["scope"]["write"] == [str(clone), f"{clone}/.claude/worktrees/**"]
    assert status["knowledge"]["status"] == "serving"


def test_error_when_check_project_fails(
    knowledge_clone: KnowledgeClone, serve: Serve, knowledge_row: KnowledgeRow, register: Register
) -> None:
    """点検で違反があれば `sources[]` を書き換えず、違反のキーのパスと理由を返す（異常シナリオ）。"""
    # 準備
    broken = _CONFIG.read_text(encoding="utf-8").replace(*_BROKEN_SCHEMA, 1)
    clone = knowledge_clone({"dev-docs.yaml": broken})
    served = serve([])
    # 実行
    result = register(served, clone, knowledge_row(clone))
    # 検証
    assert result.reload is None
    assert served.sources() == []
    assert result.check.data["violations"] == [
        {
            "path": "documents[0].schema",
            "rule": "スキーマのファイルが無い: schemas/missing.schema.yaml",
        }
    ]
