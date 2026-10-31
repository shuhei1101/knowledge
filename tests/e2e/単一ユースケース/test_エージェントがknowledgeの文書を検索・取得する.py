"""エージェントが knowledge の文書を検索・取得する（SC-72-4）の E2E テスト。"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。起動した dev-docs は conftest の Served、ツールの結果は conftest の ToolResult
type Served = Any
type ToolResult = Any
type KnowledgeClone = Callable[..., Path]
type Serve = Callable[..., Any]
type KnowledgeRow = Callable[..., Any]

# 規約を引くタグと、files.yaml の行の Markdown を引く名前
_TAG = "topic:文章"
_SKILL_NAME = "文章の点検"
_SKILL_ID = "skills/text-review/SKILL"


def _search(
    served: Served, cwd: Path, field: str, op: str, value: str, view: str = "summary"
) -> ToolResult:
    """作業場所 cwd から、knowledge の文書を 1 つの条件で検索する。"""
    return served.call(
        "search_docs",
        source="knowledge",
        cwd=str(cwd),
        filter={"field": field, "op": op, "values": [value]},
        view=view,
        fields=["name", "description", "tags"],
        format="json",
    )


def test_normal(
    knowledge_clone: KnowledgeClone, serve: Serve, knowledge_row: KnowledgeRow, tmp_path: Path
) -> None:
    """クローンの外の作業場所から規約と files.yaml の行の Markdown を引き、本文を取得する（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    served = serve([knowledge_row(clone)])
    other = tmp_path / "other-repo"
    other.mkdir()
    # 実行
    rules = _search(served, other, "tags", "contains", _TAG)
    skills = _search(served, other, "name", "contains", _SKILL_NAME)
    body = _search(served, other, "id", "eq", _SKILL_ID, view="full")
    # 検証
    items = rules.data["items"]
    assert not rules.is_error
    assert items
    assert {item["values"]["kind"] for item in items} >= {"rule"}
    assert all(item["values"].keys() >= {"name", "description", "tags"} for item in items)
    assert [item["id"] for item in skills.data["items"]] == [_SKILL_ID]
    assert body.data["items"][0]["values"]["body"] == (
        clone / "skills" / "text-review" / "SKILL.md"
    ).read_text(encoding="utf-8")


def test_error_when_out_of_read_scope(
    knowledge_clone: KnowledgeClone, serve: Serve, knowledge_row: KnowledgeRow, tmp_path: Path
) -> None:
    """scope.read の外の作業場所には knowledge の文書を返さない（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    served = serve([knowledge_row(clone, read=[str(clone), f"{clone}/**"])])
    other = tmp_path / "other-repo"
    other.mkdir()
    # 実行
    result = _search(served, other, "tags", "contains", _TAG)
    # 検証
    assert result.is_error
    assert "SourceNotReadableError" in result.text
    assert f"knowledge はこの作業場所（{other}）から読めません" in result.text
