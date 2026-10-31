"""エージェントが knowledge の文書を書き込む（SC-72-5）の E2E テスト。"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

# conftest の fixture の型。起動した dev-docs は conftest の Served、ツールの結果は conftest の ToolResult
type Served = Any
type ToolResult = Any
type KnowledgeClone = Callable[..., Path]
type Serve = Callable[..., Any]
type KnowledgeRow = Callable[..., Any]
type KnowledgeWorktree = Callable[[Path], Path]

# 書き込む規約の ID と、書き込まれる先
_DOC_ID = "e2e-sample"
_DOC_FILE = Path("docs/rule") / f"{_DOC_ID}.yaml"
# 違反の無い mermaid と、subgraph の end が抜けた mermaid
_VALID_MERMAID = "```mermaid\nflowchart TD\n  A --> B\n```"
_BROKEN_MERMAID = "```mermaid\nflowchart TD\n  subgraph S\n    A --> B\n```"


def _rule(body: str) -> dict[str, Any]:
    """スキーマに合う規約の文書を、概要の本文を渡して作る。"""
    return {
        "id": _DOC_ID,
        "kind": "rule",
        "name": "E2E の規約",
        "description": "E2E で書き込む規約を定め、E2E のときに読む。",
        "tags": [{"name": "scope:dev", "main": True}],
        "status": "current",
        "visibility": "internal",
        "rev": 1,
        "last_reviewed": "2026-10-31",
        "items": [{"id": "overview", "name": "概要", "body": f"E2E の本文。\n\n{body}"}],
    }


def _write(served: Served, document: dict[str, Any], workplace: Path) -> ToolResult:
    """作業場所 workplace から規約を 1 つ作る。"""
    return served.call(
        "write_docs",
        operations=[{"op": "create", "kind": "rule", "data": document}],
        source="knowledge",
        worktree=str(workplace),
        cwd=str(workplace),
    )


def test_normal(
    knowledge_clone: KnowledgeClone,
    knowledge_worktree: KnowledgeWorktree,
    serve: Serve,
    knowledge_row: KnowledgeRow,
) -> None:
    """違反の無い規約を worktree に書き込む（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    worktree = knowledge_worktree(clone)
    served = serve([knowledge_row(clone)])
    document = _rule(_VALID_MERMAID)
    # 実行
    result = _write(served, document, worktree)
    # 検証
    assert not result.is_error
    assert result.data["applied"] is True
    assert result.data["results"][0]["status"] == "created"
    assert YAML(typ="safe").load((worktree / _DOC_FILE).read_text(encoding="utf-8")) == document


def test_error_when_validator_reports_violation(
    knowledge_clone: KnowledgeClone,
    knowledge_worktree: KnowledgeWorktree,
    serve: Serve,
    knowledge_row: KnowledgeRow,
) -> None:
    """mermaid の誤りを検査のスクリプトが返すと、書き込まずに違反を返す（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    worktree = knowledge_worktree(clone)
    served = serve([knowledge_row(clone)])
    # 実行
    result = _write(served, _rule(_BROKEN_MERMAID), worktree)
    # 検証
    assert result.is_error
    assert "ValidationFailedError" in result.text
    assert "operations[0].items[0].body" in result.text
    assert "knowledge-checks: " in result.text
    assert " 行目: mermaid: " in result.text
    assert not (worktree / _DOC_FILE).exists()


def test_error_when_out_of_write_scope(
    knowledge_clone: KnowledgeClone, serve: Serve, knowledge_row: KnowledgeRow, tmp_path: Path
) -> None:
    """scope.write の外の作業場所からは書き込まずに断る（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    served = serve([knowledge_row(clone)])
    other = tmp_path / "other-repo"
    other.mkdir()
    # 実行
    result = _write(served, _rule(_VALID_MERMAID), other)
    # 検証
    assert result.is_error
    assert "SourceNotWritableError" in result.text
    assert f"knowledge にはこの作業場所（{other}）から書き込めません" in result.text
    assert not (clone / _DOC_FILE).exists()
    assert not (other / _DOC_FILE).exists()
