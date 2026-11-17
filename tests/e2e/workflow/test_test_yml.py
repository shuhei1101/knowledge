"""テストの全件実行のワークフロー（.github/workflows/test.yml）の結合テスト。本物の GitHub Actions で起動して確認する。"""

import re
from collections.abc import Callable, Mapping
from pathlib import Path

# 起動する workflow のファイル名
WORKFLOW = "test.yml"

# ログを上げる成果物の名前と、その中のファイル名
ARTIFACT = "test-log"
LOG_FILE = "test.log"

# workflow のファイルの step の名前。GitHub が追加する step（Set up job 等）は確認しない
STEPS = (
    "ブランチを取得する",
    "uv を入れる",
    "Node を入れる",
    "lint の道具を入れる",
    "層の全件を回す",
    "ログを成果物に上げる",
)

# pytest の最終行の集計
_SUMMARY = re.compile(r"^=+ .*\d+ (passed|failed).* in [\d.]+s .*=+$", re.MULTILINE)

# 検証用のブランチを push する前に、worktree へ適用する変更
type Mutation = Callable[[Path], None]

# 検証用のブランチを作る関数（branch_factory の fixture）
type BranchFactory = Callable[[Mutation | None], str]

# workflow を起動して、実行の ID・結論・step ごとの結論を返却する関数（workflow_runner の fixture）
type WorkflowRunner = Callable[[str, str, Mapping[str, str]], tuple[str, str, dict[str, str]]]

# 成果物の中のファイルの本文を返却する関数（artifact_reader の fixture）
type ArtifactReader = Callable[[str, str, str], str]


def _assert_steps(steps: Mapping[str, str], expected: Mapping[str, str]) -> None:
    """図の step が期待した結論で通り、図に無い step が skipped かを確認する。"""
    for name in STEPS:
        assert steps.get(name) == expected.get(name, "skipped"), name


def _add_failing_test(worktree: Path) -> None:
    """tests/unit/ に必ず失敗するテストを 1 件追加する。"""
    (worktree / "tests/unit/test_always_fail.py").write_text(
        '"""検証用に必ず失敗するテスト。"""\n\n\n'
        "def test_always_fail() -> None:\n"
        '    """必ず失敗する。"""\n'
        "    assert False\n",
        encoding="utf-8",
    )


def _remove_lint_lock(worktree: Path) -> None:
    """scripts/lint/package-lock.json を削除し、npm ci を失敗させる。"""
    (worktree / "scripts/lint/package-lock.json").unlink()


def test_normal(
    branch_factory: BranchFactory, workflow_runner: WorkflowRunner, artifact_reader: ArtifactReader
) -> None:
    """層の全件が成功し、ログを成果物に上げて成功で終わる（正常系）。"""
    # 準備
    branch = branch_factory(None)

    # 実行
    run_id, conclusion, steps = workflow_runner(WORKFLOW, branch, {"layer": "unit"})

    # 検証
    assert conclusion == "success"
    _assert_steps(
        steps,
        {
            "ブランチを取得する": "success",
            "uv を入れる": "success",
            "層の全件を回す": "success",
            "ログを成果物に上げる": "success",
        },
    )
    log = artifact_reader(run_id, ARTIFACT, LOG_FILE)
    assert _SUMMARY.search(log) is not None


def test_normal_when_integration(
    branch_factory: BranchFactory, workflow_runner: WorkflowRunner, artifact_reader: ArtifactReader
) -> None:
    """lint の道具を入れてから結合テストの層の全件を回し、成功で終わる（正常系）。"""
    # 準備
    branch = branch_factory(None)

    # 実行
    run_id, conclusion, steps = workflow_runner(WORKFLOW, branch, {"layer": "integration"})

    # 検証
    assert conclusion == "success"
    _assert_steps(
        steps,
        {
            "ブランチを取得する": "success",
            "uv を入れる": "success",
            "Node を入れる": "success",
            "lint の道具を入れる": "success",
            "層の全件を回す": "success",
            "ログを成果物に上げる": "success",
        },
    )
    log = artifact_reader(run_id, ARTIFACT, LOG_FILE)
    assert _SUMMARY.search(log) is not None


def test_error_when_tests_fail(
    branch_factory: BranchFactory, workflow_runner: WorkflowRunner, artifact_reader: ArtifactReader
) -> None:
    """層のテストが 1 件失敗し、ログを成果物に上げて失敗で終わる（異常系）。"""
    # 準備
    branch = branch_factory(_add_failing_test)

    # 実行
    run_id, conclusion, steps = workflow_runner(WORKFLOW, branch, {"layer": "unit"})

    # 検証
    assert conclusion == "failure"
    _assert_steps(
        steps,
        {
            "ブランチを取得する": "success",
            "uv を入れる": "success",
            "層の全件を回す": "failure",
            "ログを成果物に上げる": "success",
        },
    )
    log = artifact_reader(run_id, ARTIFACT, LOG_FILE)
    assert "test_always_fail" in log
    summary = _SUMMARY.search(log)
    assert summary is not None
    assert "failed" in summary[0]


def test_error_when_setup_fails(
    branch_factory: BranchFactory, workflow_runner: WorkflowRunner
) -> None:
    """lint の道具を入れられず、層の全件を回さずに失敗で終わる（異常系）。"""
    # 準備
    branch = branch_factory(_remove_lint_lock)

    # 実行
    _, conclusion, steps = workflow_runner(WORKFLOW, branch, {"layer": "integration"})

    # 検証
    assert conclusion == "failure"
    _assert_steps(
        steps,
        {
            "ブランチを取得する": "success",
            "uv を入れる": "success",
            "Node を入れる": "success",
            "lint の道具を入れる": "failure",
            "ログを成果物に上げる": "success",
        },
    )
