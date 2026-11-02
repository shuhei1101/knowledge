"""利用者が端末に knowledge を導入して規約を引く（SC-72-1）の E2E テスト。"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。起動した dev-docs は conftest の Served
type KnowledgeClone = Callable[..., Path]
type Serve = Callable[..., Any]
type KnowledgeRow = Callable[..., Any]
type Register = Callable[..., Any]
type RepresentativePages = Callable[[Path], dict[str, str]]

# リポジトリの直下の dev-docs.yaml
_CONFIG = Path(__file__).resolve().parents[3] / "dev-docs.yaml"
# documents の先頭の行のスキーマを、存在しないファイルへ向ける置き換え
_BROKEN_SCHEMA = ("schema: schemas/rule.schema.yaml", "schema: schemas/missing.schema.yaml")
# 規約を引くタグ
_TAG = "topic:文章"


def test_normal(
    knowledge_clone: KnowledgeClone,
    serve: Serve,
    knowledge_row: KnowledgeRow,
    register: Register,
    representative_pages: RepresentativePages,
    tmp_path: Path,
) -> None:
    """登録した knowledge の文書を、画面とクローンの外の作業場所の MCP で引ける（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    served = serve([])
    other = tmp_path / "other-repo"
    other.mkdir()
    # 実行
    # 登録: 点検 → 端末の設定への記載 → 読み直し → 状態の確認
    registration = register(served, clone, knowledge_row(clone))
    # 画面: 文書の行ごとに先頭の文書を開く
    pages = {
        kind: served.open_page("knowledge", path)
        for kind, path in representative_pages(clone).items()
    }
    # MCP: クローンの外の作業場所から規約を引く
    found = served.call(
        "search_docs",
        source="knowledge",
        cwd=str(other),
        filter={"field": "tags", "op": "contains", "values": [_TAG]},
        view="summary",
        format="json",
    )
    # 検証
    sources = served.sources()
    assert "violations" not in registration.check.data
    assert [source["id"] for source in sources] == ["knowledge"]
    assert sources[0]["scope"]["read"] == ["/**"]
    assert sources[0]["scope"]["write"] == [str(clone), f"{clone}/.claude/worktrees/**"]
    assert {kind: page.status for kind, page in pages.items()} == dict.fromkeys(pages, 200)
    assert [kind for kind, page in pages.items() if not page.body["markdown"].strip()] == []
    assert not found.is_error
    assert found.data["items"]


def test_error_when_setup_check_fails(
    knowledge_clone: KnowledgeClone, serve: Serve, knowledge_row: KnowledgeRow, register: Register
) -> None:
    """登録の点検で誤りがあれば `sources[]` を書き換えず、誤りのあるファイルと内容を返す（異常シナリオ）。"""
    # 準備
    broken = _CONFIG.read_text(encoding="utf-8").replace(*_BROKEN_SCHEMA, 1)
    clone = knowledge_clone({"dev-docs.yaml": broken})
    served = serve([])
    # 実行
    registration = register(served, clone, knowledge_row(clone))
    # 検証
    violations = registration.check.data["violations"]
    assert registration.reload is None
    assert served.sources() == []
    assert [violation["path"] for violation in violations] == ["documents[0].schema"]
    assert "schemas/missing.schema.yaml" in violations[0]["rule"]
