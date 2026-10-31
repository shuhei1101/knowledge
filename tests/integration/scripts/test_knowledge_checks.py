"""文書の違反の検査（scripts/knowledge_checks.py）の結合テスト。"""

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]
type RepoFactory = Callable[[dict[str, str]], Path]
type RunChecksWithLimit = Callable[[Path, str, float], Any]

# 項目 x を持つ配信元の文書
_DOC_A = "id: a\nkind: rule\nname: A\ndescription: A の文書\nitems:\n  - id: x\n    name: X\n    body: 本文\n"


def _hashes(root: Path) -> dict[str, str]:
    """フォルダの配下の全てのファイルのハッシュを返す。"""
    return {
        str(file.relative_to(root)): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in sorted(root.rglob("*"))
        if file.is_file()
    }


def test_normal(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """違反の無い文書に空の配列を返す（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/a.yaml": _DOC_A})
    before = _hashes(root)
    stdin = (
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: |-\n"
        "      [A](id:a#x)\n"
        "\n"
        "      ```mermaid\n"
        "      flowchart TD\n"
        "        A --> B\n"
        "      ```\n"
        "related:\n"
        "  - to: a\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []
    assert _hashes(root) == before


def test_normal_when_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """項目の ID の重複・参照切れ・mermaid の誤りを全て配列で返す（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/a.yaml": _DOC_A})
    stdin = (
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: 本文\n"
        "  - id: p\n"
        "    body: 本文\n"
        "  - id: q\n"
        "    body: '[B](id:missing)'\n"
        "  - id: r\n"
        "    body: |-\n"
        "      ```mermaid\n"
        "      flowchart TD\n"
        "        subgraph S\n"
        "          A --> B\n"
        "      ```\n"
        "related:\n"
        "  - to: missing\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [v["path"] for v in violations] == [
        "items[1].id",
        "items[2].body",
        "related[0].to",
        "items[3].body",
    ]
    assert violations[3]["rule"].startswith("14 行目: mermaid: ")


def test_normal_when_timed_out(
    run_checks_with_limit: RunChecksWithLimit, repo_factory: RepoFactory
) -> None:
    """残り時間が足りない mermaid のブロックを時間切れの違反として返す（正常系）。"""
    # 準備
    root = repo_factory({})
    stdin = (
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: |-\n"
        "      ```mermaid\n"
        "      flowchart TD\n"
        "        A --> B\n"
        "      ```\n"
    )
    # 実行
    result = run_checks_with_limit(root, stdin, 1.0)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [v["path"] for v in violations] == ["items[0].body"]
    assert "処理時間の上限" in violations[0]["rule"]
    assert result.elapsed_sec <= 2.0


def test_normal_when_invalid_yaml(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """読めない入力を path: $ の違反 1 件で返す（正常系）。"""
    # 準備
    root = repo_factory({})
    stdin = "items:\n  - id: a\n    name: [\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert len(violations) == 1
    assert violations[0]["path"] == "$"
    assert " 行目: " in violations[0]["rule"]


def test_error_when_maid_missing(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """maid が PATH から引けなければ検査を始めずに終わる（異常系）。"""
    # 準備
    root = repo_factory({})
    # 実行
    result = run_script("knowledge_checks", root, "id: self\n", without_maid=True)
    # 検証
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "maid が PATH にありません" in result.stderr
    assert "環境構築" in result.stderr
