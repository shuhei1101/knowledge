"""開発者が文書の違反を検査する（SC-72-6）の E2E テスト。"""

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。子プロセスの結果は subprocess.CompletedProcess
type KnowledgeClone = Callable[..., Path]
type RunCheckAll = Callable[..., Any]

# 違反の文書の元にする、違反の無い規約
_SOURCE = Path(__file__).resolve().parents[3] / "docs" / "rule" / "dev-precheck.yaml"
# 項目の ID が重複した文書と、スキーマに合わない（status が許す値の外）文書の置き場所
_DUPLICATED = "docs/rule/e2e-duplicated.yaml"
_INVALID = "docs/rule/e2e-invalid.yaml"
# 最後の行の集計
_SUMMARY = re.compile(r"^(\d+) 件の文書を検査し、違反は (\d+) 件でした$")


def _violation_documents() -> dict[str, str]:
    """違反を持つ 2 つの文書を返す。"""
    source = _SOURCE.read_text(encoding="utf-8")
    duplicated = source.replace("id: dev-precheck", "id: e2e-duplicated", 1).replace(
        "  - id: check-target-02", "  - id: check-target-01", 1
    )
    invalid = source.replace("id: dev-precheck", "id: e2e-invalid", 1).replace(
        "status: current", "status: unknown", 1
    )
    return {_DUPLICATED: duplicated, _INVALID: invalid}


def test_normal(knowledge_clone: KnowledgeClone, run_check_all: RunCheckAll) -> None:
    """違反の無い文書だけなら検査が成功で終わる（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    # 実行
    result = run_check_all(clone)
    # 検証
    summary = _SUMMARY.match(result.stdout.splitlines()[-1])
    assert result.returncode == 0
    assert summary is not None
    assert summary.group(2) == "0"


def test_error_when_documents_have_violations(
    knowledge_clone: KnowledgeClone, run_check_all: RunCheckAll
) -> None:
    """違反のある文書を含めば、2 つの文書の違反を文書のパス・行・項目・内容つきで出して失敗する（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone(_violation_documents())
    # 実行
    result = run_check_all(clone)
    # 検証
    lines = result.stdout.splitlines()
    summary = _SUMMARY.match(lines[-1])
    assert result.returncode == 1
    assert summary is not None
    assert int(summary.group(2)) == len(lines) - 1
    assert re.search(
        rf"^{re.escape(_DUPLICATED)}:\d+: items\[\d+\]\.id: .+重複", result.stdout, re.MULTILINE
    )
    assert re.search(
        rf"^{re.escape(_INVALID)}:\d+: status: schema: .+unknown", result.stdout, re.MULTILINE
    )


def test_error_when_maid_missing(
    knowledge_clone: KnowledgeClone, run_check_all: RunCheckAll
) -> None:
    """maid が PATH から引けなければ、文書の検査を始めずに失敗する（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    # 実行
    result = run_check_all(clone, without_maid=True)
    # 検証
    assert result.returncode == 2
    assert result.stdout == ""
    assert "maid が PATH にありません" in result.stderr
