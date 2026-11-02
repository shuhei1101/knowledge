"""全ての文書の検査（scripts/check_all.py）の結合テスト。"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]
type RepoFactory = Callable[[dict[str, str]], Path]


def test_normal(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """違反の無い文書だけなら終了コード 0 で終わる（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/a.yaml": "id: a\nkind: rule\nname: A\ndescription: A の文書\nitems:\n  - id: x\n    body: '[B](id:b)'\n",
            "docs/rule/b.yaml": "id: b\nkind: rule\nname: B\ndescription: B の文書\nitems:\n  - id: y\n    body: 本文\n",
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout.splitlines()[-1] == "2 件の文書を検査し、違反は 0 件でした"


def test_normal_when_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """全ての文書を検査し終えてから、全ての違反を出して終了コード 1 で終わる（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/a.yaml": "id: a\nkind: rule\nname: A\nitems:\n  - id: x\n    body: 本文\n",
            "docs/rule/b.yaml": "id: b\nkind: rule\nname: B\ndescription: B の文書\nitems:\n  - id: y\n    body: 本文\n  - id: y\n    body: 本文\n",
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    lines = result.stdout.splitlines()
    assert result.exit_code == 1
    assert lines[0].startswith("docs/rule/a.yaml:1: $: ")
    assert "description" in lines[0]
    assert lines[1].startswith("docs/rule/b.yaml:8: items[1].id: ")
    assert lines[-1] == "2 件の文書を検査し、違反は 2 件でした"


def test_error_when_maid_missing(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """maid が PATH から引けなければ検査を始めずに終わる（異常系）。"""
    # 準備
    root = repo_factory({})
    # 実行
    result = run_script("check_all", root, without_maid=True)
    # 検証
    assert result.exit_code == 2
    assert "maid が PATH にありません" in result.stderr


def test_error_when_config_missing(run_script: RunScript, tmp_path: Path) -> None:
    """dev-docs.yaml が無いか読めなければ検査を始めずに終わる（異常系）。"""
    # 準備
    root = tmp_path / "empty"
    root.mkdir()
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 2
    assert "dev-docs.yaml" in result.stderr
