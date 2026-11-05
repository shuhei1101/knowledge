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
            "docs/rule/b.yaml": "id: b\nkind: rule\nname: B\ndescription: B の文書\nitems:\n  - id: y\n    body: 本文。\n",
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout.splitlines()[-1] == "2 件の文書を検査し、違反は 0 件、警告は 0 件でした"


def test_normal_when_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """全ての文書を検査し終えてから、全ての違反を出して終了コード 1 で終わる（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/a.yaml": "id: a\nkind: rule\nname: A\nitems:\n  - id: x\n    body: 本文。\n",
            "docs/rule/b.yaml": "id: b\nkind: rule\nname: B\ndescription: B の文書\nitems:\n  - id: y\n    body: 本文。\n  - id: y\n    body: 本文。\n",
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
    assert lines[-1] == "2 件の文書を検査し、違反は 2 件、警告は 0 件でした"


def test_normal_when_lint_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """失敗させるルールの lint の違反を、元の文書の YAML の行で出して終了コード 1 で終わる（正常系）。"""
    # 準備
    root = repo_factory(
        {
            # items[0].body の 3 行目（文書の 10 行目）が太字だけの段落
            "docs/rule/a.yaml": (
                "id: a\n"
                "kind: rule\n"
                "name: A\n"
                "description: A の文書\n"
                "items:\n"
                "  - id: x\n"
                "    body: |-\n"
                "      本文。\n"
                "\n"
                "      **太字だけの段落**\n"
            ),
            # 4 行目の引用符の無い値の # 以降がコメントになる
            "docs/rule/b.yaml": (
                "id: b\nkind: rule\nname: B\ndescription: B の文書 #bar\nitems:\n"
                "  - id: y\n    body: 本文。\n"
            ),
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    lines = result.stdout.splitlines()
    assert result.exit_code == 1
    assert any(
        line.startswith("docs/rule/a.yaml:10: items[0].body: markdownlint/MD036: ")
        for line in lines
    )
    assert any(line.startswith("docs/rule/b.yaml:4: -: yamllint/comments: ") for line in lines)


def test_normal_when_only_warnings(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """警告にしたルールの違反は警告の行として出し、終了コードには数えない（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/a.yaml": (
                "id: a\nkind: rule\nname: A\ndescription: A の文書\nitems:\n"
                "  - id: x\n    body: A です。B です。\n"
            ),
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    lines = result.stdout.splitlines()
    assert result.exit_code == 0
    assert any(
        line.startswith(
            "docs/rule/a.yaml:7: items[0].body: warning: textlint/one-sentence-per-line: "
        )
        for line in lines
    )
    assert lines[-1] == "1 件の文書を検査し、違反は 0 件、警告は 1 件でした"


def test_normal_when_word_list_copy_stale(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """対応表のコピーが正本から作り直したものと違えば、違反として出す（正常系）。"""
    # 準備
    word_list = (
        "id: word-list-ai-slop\n"
        "kind: word-list\n"
        "name: 対応表\n"
        "description: 対応表の文書\n"
        "entries:\n"
        "  - id: naosu\n"
        "    ng: 直す\n"
        "    ok: [修正]\n"
        "  - id: tasu\n"
        "    ng: 足す\n"
        "    ok: [追加]\n"
    )
    # コピーは正本の 1 行を除いたもの
    stale = '{\n  "entries": [\n    {\n      "id": "naosu",\n      "ng": "直す",\n      "ok": [\n        "修正"\n      ]\n    }\n  ]\n}\n'
    root = repo_factory(
        {
            "docs/word-list/word-list-ai-slop.yaml": word_list,
            "plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json": stale,
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 1
    line = next(
        line
        for line in result.stdout.splitlines()
        if line.startswith("plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json")
    )
    assert "scripts/build_word_list.py" in line


def test_error_when_check_cli_missing(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """maid・markdownlint-cli2・textlint のどれかが引けなければ検査を始めずに終わる（異常系）。"""
    # 準備
    root = repo_factory({})
    missing = tmp_path / "missing-lint"
    # 実行
    result = run_script("check_all", root, without_maid=True, args=["--lint-dir", str(missing)])
    # 検証
    assert result.exit_code == 2
    assert result.stderr.splitlines() == [
        "maid がありません。開発コマンドの『環境構築（クローン直後）』で入れてください",
        "markdownlint-cli2 がありません。開発コマンドの『環境構築（クローン直後）』で入れてください",
        "textlint がありません。開発コマンドの『環境構築（クローン直後）』で入れてください",
    ]


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
