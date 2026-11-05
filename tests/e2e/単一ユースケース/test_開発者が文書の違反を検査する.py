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
# 段落全体が太字の段落を含む文書と、引用符の無い値の後ろに ` #` を続けた行を含む文書の置き場所
_BOLD = "docs/rule/e2e-bold.yaml"
_COMMENT = "docs/rule/e2e-comment.yaml"
# 太字だけの段落
_BOLD_PARAGRAPH = "**太字だけの段落**"
# 最後の行の集計
_SUMMARY = re.compile(r"^(\d+) 件の文書を検査し、違反は (\d+) 件、警告は (\d+) 件でした$")
# 警告の行の目印
_WARNING = ": warning: "


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


def _lint_violation_documents() -> tuple[dict[str, str], int, int]:
    """書式の違反を持つ 2 つの文書と、太字だけの段落の行・コメントになる行の行番号を返す。"""
    source = _SOURCE.read_text(encoding="utf-8")
    # items[0].body の末尾に太字だけの段落を加える
    bold = source.replace("id: dev-precheck", "id: e2e-bold", 1).replace(
        "      入力の妥当性の検査とは別に扱う。\n",
        f"      入力の妥当性の検査とは別に扱う。\n\n      {_BOLD_PARAGRAPH}\n",
        1,
    )
    # description の引用符の無い値の後ろに ` #bar` を続ける
    lines = source.replace("id: dev-precheck", "id: e2e-comment", 1).splitlines()
    comment_line = next(i for i, line in enumerate(lines) if line.startswith("description: "))
    lines[comment_line] += " #bar"
    bold_line = bold.splitlines().index(f"      {_BOLD_PARAGRAPH}")
    documents = {_BOLD: bold, _COMMENT: "\n".join(lines) + "\n"}
    return documents, bold_line + 1, comment_line + 1


def _violation_lines(lines: list[str]) -> list[str]:
    """最後の行の集計と警告の行を除いた、違反の行を返す。"""
    return [line for line in lines[:-1] if _WARNING not in line]


def _violation_paths(lines: list[str]) -> set[str]:
    """違反の行の文書のパスを返す。"""
    return {line.split(":", 1)[0] for line in _violation_lines(lines)}


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
    assert _violation_lines(result.stdout.splitlines()) == []


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
    assert int(summary.group(2)) == len(_violation_lines(lines))
    assert _violation_paths(lines) == {_DUPLICATED, _INVALID}
    assert re.search(
        rf"^{re.escape(_DUPLICATED)}:\d+: items\[\d+\]\.id: .+重複", result.stdout, re.MULTILINE
    )
    assert re.search(
        rf"^{re.escape(_INVALID)}:\d+: status: schema: .+unknown", result.stdout, re.MULTILINE
    )


def test_error_when_documents_have_lint_violations(
    knowledge_clone: KnowledgeClone, run_check_all: RunCheckAll
) -> None:
    """書式の違反を含めば、2 つの文書の違反を文書のパス・元の YAML の行・ルール名つきで出して失敗する（異常シナリオ）。"""
    # 準備
    documents, bold_line, comment_line = _lint_violation_documents()
    clone = knowledge_clone(documents)
    # 実行
    result = run_check_all(clone)
    # 検証
    lines = result.stdout.splitlines()
    summary = _SUMMARY.match(lines[-1])
    violations = _violation_lines(lines)
    assert result.returncode == 1
    assert summary is not None
    assert int(summary.group(2)) == len(violations)
    assert _violation_paths(lines) == {_BOLD, _COMMENT}
    assert any(
        line.startswith(f"{_BOLD}:{bold_line}: items[0].body: markdownlint/MD036: ")
        for line in violations
    )
    assert any(
        line.startswith(f"{_COMMENT}:{comment_line}: -: yamllint/comments: ") for line in violations
    )


def test_error_when_check_cli_missing(
    knowledge_clone: KnowledgeClone, run_check_all: RunCheckAll
) -> None:
    """maid が PATH から引けなければ、maid の名前を出して文書の検査を始めずに失敗する（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    # 実行
    result = run_check_all(clone, without_maid=True)
    # 検証
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.splitlines() == [
        "maid がありません。開発コマンドの『環境構築（クローン直後）』で入れてください"
    ]
