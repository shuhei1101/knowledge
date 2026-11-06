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
# 自分の examples に合わない設計書のスキーマと、無い $defs を $ref で指す設計書のスキーマの置き場所
_BAD_EXAMPLE = "schemas/design/e2e-bad-example.schema.yaml"
_BAD_REF = "schemas/design/e2e-bad-ref.schema.yaml"
# x-rules が配列でない設計書のスキーマの置き場所
_BAD_RULES = "schemas/design/e2e-bad-rules.schema.yaml"
# ER 図のスキーマと、そのテンプレート。スキーマの id のキーの x-rules の行
_ER_SCHEMA = "schemas/design/er.schema.yaml"
_ER_TEMPLATE = "docs/template/template-er.yaml"
_ID_RULE = "      - 設計書を作るときに振り、改名・移動でも変えない。\n"
# 太字だけの段落
_BOLD_PARAGRAPH = "**太字だけの段落**"
# 最後の行の集計
_SUMMARY = re.compile(r"^(\d+) 件の文書を検査し、違反は (\d+) 件、警告は (\d+) 件でした$")
# 警告の行の目印
_WARNING = ": warning: "
# 標準エラーの、CLI の欠けの行の目印
_CLI_MISSING = "がありません。"


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


def test_error_when_design_schemas_are_invalid(
    knowledge_clone: KnowledgeClone, run_check_all: RunCheckAll
) -> None:
    """誤りのある設計書のスキーマを含めば、3 つの誤りをスキーマのパス・行・項目・内容つきで出して失敗する（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone(
        {
            # 10 行目の examples[0] が required の summary を持たない
            _BAD_EXAMPLE: (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 例の誤り\n"
                "type: object\n"
                "required:\n"
                "  - summary\n"
                "properties:\n"
                "  summary:\n"
                "    $ref: common.schema.yaml#/$defs/summary\n"
                "examples:\n"
                "  - title: x\n"
            ),
            # 5 行目の $ref が共通の型に無い $defs を指す
            _BAD_REF: (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 参照の誤り\n"
                "properties:\n"
                "  summary:\n"
                "    $ref: common.schema.yaml#/$defs/e2e-missing\n"
            ),
            # 3 行目の x-rules が配列でない
            _BAD_RULES: (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 決まりの誤り\n"
                "x-rules: 文字列\n"
            ),
        }
    )
    # 実行
    result = run_check_all(clone)
    # 検証
    lines = result.stdout.splitlines()
    summary = _SUMMARY.match(lines[-1])
    assert result.returncode == 1
    assert summary is not None
    assert int(summary.group(2)) == len(_violation_lines(lines))
    assert _violation_paths(lines) == {_BAD_EXAMPLE, _BAD_REF, _BAD_RULES}
    assert any(
        line.startswith(f"{_BAD_RULES}:3: x-rules: metaschema: ")
        for line in _violation_lines(lines)
    )
    assert any(
        line.startswith(f"{_BAD_EXAMPLE}:10: examples[0]: examples: ")
        for line in _violation_lines(lines)
    )
    assert any(
        line.startswith(
            f"{_BAD_REF}:5: properties.summary.$ref: $ref: common.schema.yaml#/$defs/e2e-missing "
        )
        for line in _violation_lines(lines)
    )


def test_error_when_templates_out_of_date(
    knowledge_clone: KnowledgeClone, run_check_all: RunCheckAll
) -> None:
    """スキーマに決まりを追加して生成し直さなければ、ずれたテンプレートと生成のコマンドを出して失敗する（異常シナリオ）。"""
    # 準備
    schema = (_SOURCE.parents[2] / _ER_SCHEMA).read_text(encoding="utf-8")
    clone = knowledge_clone(
        {_ER_SCHEMA: schema.replace(_ID_RULE, f"{_ID_RULE}      - e2e で追加した決まり。\n", 1)}
    )
    # 実行
    result = run_check_all(clone)
    # 検証
    lines = result.stdout.splitlines()
    assert result.returncode == 1
    assert _violation_paths(lines) == {_ER_TEMPLATE}
    line = next(line for line in _violation_lines(lines) if line.startswith(f"{_ER_TEMPLATE}:"))
    assert _ER_SCHEMA in line
    assert "scripts/build_templates.py" in line


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
    # uv が依存を入れたときの行はキャッシュの状態で出るため、CLI の欠けの行だけを比べる
    missing = [line for line in result.stderr.splitlines() if _CLI_MISSING in line]
    assert missing == [
        "maid がありません。開発コマンドの『環境構築（クローン直後）』で入れてください"
    ]
