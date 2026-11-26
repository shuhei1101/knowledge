"""scripts/_lint.py の単体テスト。"""

import sys
import textwrap
from collections.abc import Callable
from pathlib import Path, PurePosixPath

import pytest

from _lint import (
    YAMLLINT_SCHEMAS_CONFIG,
    LintFinding,
    LintOutputError,
    LintSource,
    MdmarkCheckError,
    collect_map_sources,
    collect_sources,
    extract_map_mermaid,
    find_lint_clis,
    load_yamllint_config,
    run_map_check,
    run_markdown_lints,
    run_yamllint,
)

# 差し替えの CLI の本体。引数の最初の .md のパスを {first} に入れて出し、決めた終了コードで終わる
_FAKE_CLI = textwrap.dedent(
    """\
    #!{python}
    import sys
    from pathlib import Path

    first = next((a for a in sys.argv[1:] if a.endswith(".md")), "")
    marker = {marker!r}
    if marker:
        Path(marker).write_text("called", encoding="utf-8")
    sys.stdout.write({stdout!r}.replace("{{first}}", first))
    sys.stderr.write({stderr!r}.replace("{{first}}", first))
    sys.exit({exit_code!r})
    """
)

# scripts/lint/.yamllint.yaml と同じ内容の設定
_YAMLLINT_CONFIG = textwrap.dedent(
    """\
    extends: default
    rules:
      comments:
        level: error
      document-start: disable
      line-length: disable
      truthy:
        check-keys: false
    """
)

# scripts/lint/.yamllint-schemas.yaml と同じ内容の設定
_YAMLLINT_SCHEMAS_CONFIG = textwrap.dedent(
    """\
    rules:
      brackets:
        forbid: non-empty
      braces:
        forbid: non-empty
    """
)

type FakeCliFactory = Callable[..., str]


@pytest.fixture
def fake_cli_factory(tmp_path: Path) -> FakeCliFactory:
    """決めた出力と終了コードで終わる CLI の差し替えを、lint のフォルダの node_modules/.bin に作る関数を返す。"""

    def _create(
        name: str,
        *,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        marker: Path | None = None,
    ) -> str:
        folder = tmp_path / "lint" / "node_modules" / ".bin"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / name
        path.write_text(
            _FAKE_CLI.format(
                python=sys.executable,
                marker=str(marker) if marker else "",
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
            ),
            encoding="utf-8",
        )
        path.chmod(0o755)
        return str(path)

    return _create


def test_find_lint_clis(tmp_path: Path, fake_cli_factory: FakeCliFactory) -> None:
    """2 つとも引ける（正常系）。"""
    # 準備
    markdownlint = fake_cli_factory("markdownlint-cli2")
    textlint = fake_cli_factory("textlint")
    # 実行
    result = find_lint_clis(tmp_path / "lint")
    # 検証
    assert result == {"markdownlint-cli2": markdownlint, "textlint": textlint}


def test_find_lint_clis_when_missing(tmp_path: Path) -> None:
    """フォルダが無い（正常系）。"""
    # 準備
    lint_dir = tmp_path / "missing"
    # 実行
    result = find_lint_clis(lint_dir)
    # 検証
    assert result == {"markdownlint-cli2": None, "textlint": None}


def test_collect_sources() -> None:
    """body の項目だけを取り出す（正常系）。"""
    # 準備
    text = (
        "id: a\n"
        "items:\n"
        "  - id: one\n"
        "    name: 一つ目\n"
        "    body: |-\n"
        "      本文 1。\n"
        "  - id: two\n"
        "    name: 二つ目\n"
        "    body: |-\n"
        "      本文 2。\n"
    )
    # 実行
    result = collect_sources(PurePosixPath("docs/rule/a.yaml"), text)
    # 検証
    assert result == [
        LintSource(PurePosixPath("docs/rule/a.yaml"), "items[0].body", 6, "本文 1。"),
        LintSource(PurePosixPath("docs/rule/a.yaml"), "items[1].body", 10, "本文 2。"),
    ]


def test_collect_sources_when_markdown_file() -> None:
    """.md の文書（正常系）。"""
    # 準備
    text = "# タイトル\n\n本文。\n"
    # 実行
    result = collect_sources(PurePosixPath("README.md"), text)
    # 検証
    assert result == [LintSource(PurePosixPath("README.md"), "-", 1, text)]


def test_collect_sources_when_broken() -> None:
    """読めない YAML（正常系）。"""
    # 準備
    text = "id: a\nitems: [\n"
    # 実行
    result = collect_sources(PurePosixPath("docs/rule/a.yaml"), text)
    # 検証
    assert result == []


def test_collect_map_sources() -> None:
    """map を含む項目だけを取り出す（正常系）。"""
    # 準備
    text = (
        "id: IF-1\n"
        "flows:\n"
        "  - name: 正常系\n"
        "    summary: 概要\n"
        "    flow: |-\n"
        "      <!-- map -->\n"
        "\n"
        "      ```mermaid\n"
        "      flowchart TD\n"
        "        a --> b\n"
        "      ```\n"
        "\n"
        "      <!-- /map -->\n"
        "overall_flow: |-\n"
        "  <!-- map -->\n"
        "\n"
        "  ```mermaid\n"
        "  flowchart TD\n"
        "    a --> b\n"
        "  ```\n"
        "\n"
        "  <!-- /map -->\n"
    )
    # 実行
    result = collect_map_sources(PurePosixPath("docs/interface/IF-1.yml.yaml"), text)
    # 検証
    assert [(source.item_path, source.start_line) for source in result] == [
        ("flows[0].flow", 6),
        ("overall_flow", 15),
    ]


def test_collect_map_sources_when_markdown_file() -> None:
    """.md の文書（正常系）。"""
    # 準備
    text = "<!-- map -->\n\n```mermaid\nflowchart TD\n  a --> b\n```\n\n<!-- /map -->\n"
    # 実行
    result = collect_map_sources(PurePosixPath("README.md"), text)
    # 検証
    assert result == []


def test_collect_map_sources_when_broken() -> None:
    """読み込めない YAML（正常系）。"""
    # 準備
    text = "id: a\nitems: [\n"
    # 実行
    result = collect_map_sources(PurePosixPath("docs/rule/a.yaml"), text)
    # 検証
    assert result == []


def test_run_map_check(fake_cli_factory: FakeCliFactory) -> None:
    """map のずれだけを元の文書の行で返却する（正常系）。"""
    # 準備
    npx = fake_cli_factory(
        "npx",
        stdout=(
            "-:10: map_invalid: 2 行目 `A->>B hello` を読めません\n"
            "-:1: legacy_mark: table のマーカーの引数が今の書き方です\n"
            "ずれ 2 件\n"
        ),
        exit_code=1,
    )
    sources = [
        LintSource(PurePosixPath("docs/a.yaml"), "flows[0].flow", 10, "1\n2\n3\n4\n5"),
        LintSource(PurePosixPath("docs/b.yaml"), "overall_flow", 40, "1\n2\n3\n4\n5"),
    ]
    # 実行
    result = run_map_check(sources, npx)
    # 検証
    assert result == [
        LintFinding(
            PurePosixPath("docs/b.yaml"),
            42,
            "overall_flow",
            "mdmark",
            "map_invalid",
            "2 行目 `A->>B hello` を読めません",
            False,
        )
    ]


def test_run_map_check_when_empty(tmp_path: Path, fake_cli_factory: FakeCliFactory) -> None:
    """map を含む項目が無い（正常系）。"""
    # 準備
    marker = tmp_path / "called.txt"
    npx = fake_cli_factory("npx", stdout="ずれ 0 件\n", marker=marker)
    # 実行
    result = run_map_check([], npx)
    # 検証
    assert result == []
    assert not marker.exists()


def test_run_map_check_when_not_checked(fake_cli_factory: FakeCliFactory) -> None:
    """点検せずに終了コード 1 で終わった（異常系）。"""
    # 準備
    npx = fake_cli_factory("npx", stderr="npm error code E404\n", exit_code=1)
    sources = [LintSource(PurePosixPath("docs/a.yaml"), "flows[0].flow", 10, "本文")]
    # 実行・検証
    with pytest.raises(MdmarkCheckError, match=r"1.*npm error code E404"):
        run_map_check(sources, npx)


def test_run_map_check_when_crashed(fake_cli_factory: FakeCliFactory) -> None:
    """終了コードが 0・1 でない（異常系）。"""
    # 準備
    npx = fake_cli_factory("npx", stdout="ずれ 0 件\n", exit_code=2)
    sources = [LintSource(PurePosixPath("docs/a.yaml"), "flows[0].flow", 10, "本文")]
    # 実行・検証
    with pytest.raises(MdmarkCheckError, match=r"2"):
        run_map_check(sources, npx)


def test_extract_map_mermaid() -> None:
    """Mermaid を取り出す（正常系）。"""
    # 準備
    text = "前文\n\n<!-- map -->\n\n```mermaid\nflowchart TD\n  a --> b\n  b --> c\n```\n\n<!-- /map -->\n"
    # 実行
    result = extract_map_mermaid(text)
    # 検証
    assert result == "flowchart TD\n  a --> b\n  b --> c"


def test_extract_map_mermaid_when_missing() -> None:
    """map が無い（正常系）。"""
    # 準備
    text = "```mermaid\nflowchart TD\n  a --> b\n```\n"
    # 実行
    result = extract_map_mermaid(text)
    # 検証
    assert result is None


def test_run_markdown_lints(tmp_path: Path, fake_cli_factory: FakeCliFactory) -> None:
    """違反を元の文書の行で返す（正常系）。"""
    # 準備
    markdownlint = fake_cli_factory(
        "markdownlint-cli2",
        stderr="{first}:3 error MD036/no-emphasis-as-heading Emphasis used instead of a heading\n",
        exit_code=1,
    )
    textlint = fake_cli_factory(
        "textlint",
        stdout=(
            '[{"filePath": "{first}", "messages": [{"line": 1, "ruleId": "one-sentence-per-line",'
            ' "severity": 1, "message": "1 行に 2 文があります"}]}]'
        ),
    )
    sources = [LintSource(PurePosixPath("docs/rule/a.yaml"), "items[0].body", 26, "本文。")]
    # 実行
    result = run_markdown_lints(
        sources, tmp_path / "lint", {"markdownlint-cli2": markdownlint, "textlint": textlint}
    )
    # 検証
    assert result == [
        LintFinding(
            PurePosixPath("docs/rule/a.yaml"),
            28,
            "items[0].body",
            "markdownlint",
            "MD036",
            "Emphasis used instead of a heading",
            False,
        ),
        LintFinding(
            PurePosixPath("docs/rule/a.yaml"),
            26,
            "items[0].body",
            "textlint",
            "one-sentence-per-line",
            "1 行に 2 文があります",
            True,
        ),
    ]


def test_run_markdown_lints_when_empty(tmp_path: Path, fake_cli_factory: FakeCliFactory) -> None:
    """当てる Markdown が無い（正常系）。"""
    # 準備
    marker = tmp_path / "called.txt"
    markdownlint = fake_cli_factory("markdownlint-cli2", marker=marker)
    textlint = fake_cli_factory("textlint", stdout="[]", marker=marker)
    # 実行
    result = run_markdown_lints(
        [], tmp_path / "lint", {"markdownlint-cli2": markdownlint, "textlint": textlint}
    )
    # 検証
    assert result == []
    assert not marker.exists()


def test_run_markdown_lints_when_crashed(tmp_path: Path, fake_cli_factory: FakeCliFactory) -> None:
    """CLI が落ちた（異常系）。"""
    # 準備
    markdownlint = fake_cli_factory("markdownlint-cli2")
    textlint = fake_cli_factory("textlint", stderr="設定を読めません\n", exit_code=2)
    sources = [LintSource(PurePosixPath("docs/rule/a.yaml"), "items[0].body", 6, "本文。")]
    clis = {"markdownlint-cli2": markdownlint, "textlint": textlint}
    # 実行・検証
    with pytest.raises(LintOutputError, match=r"textlint.*2.*設定を読めません"):
        run_markdown_lints(sources, tmp_path / "lint", clis)


def test_load_yamllint_config(tmp_path: Path) -> None:
    """設定を読む（正常系）。"""
    # 準備
    (tmp_path / ".yamllint.yaml").write_text(_YAMLLINT_CONFIG, encoding="utf-8")
    # 実行
    config = load_yamllint_config(tmp_path)
    # 検証
    enabled = {rule.ID for rule in config.enabled_rules(None)}
    assert "comments" in enabled
    assert "document-start" not in enabled
    assert "line-length" not in enabled


def test_load_yamllint_config_when_schemas(tmp_path: Path) -> None:
    """スキーマの設定を読む（正常系）。"""
    # 準備
    (tmp_path / ".yamllint-schemas.yaml").write_text(_YAMLLINT_SCHEMAS_CONFIG, encoding="utf-8")
    # 実行
    config = load_yamllint_config(tmp_path, YAMLLINT_SCHEMAS_CONFIG)
    # 検証
    enabled = {rule.ID for rule in config.enabled_rules(None)}
    assert {"brackets", "braces"} <= enabled
    assert "indentation" not in enabled
    assert "comments" not in enabled


def test_run_yamllint(tmp_path: Path) -> None:
    """コメントの違反（正常系）。"""
    # 準備
    (tmp_path / ".yamllint.yaml").write_text(_YAMLLINT_CONFIG, encoding="utf-8")
    config = load_yamllint_config(tmp_path)
    # 実行
    result = run_yamllint(PurePosixPath("rules.yaml"), "key: foo #bar\n", config)
    # 検証
    assert [(f.line, f.item_path, f.tool, f.rule, f.warning) for f in result] == [
        (1, "-", "yamllint", "comments", False),
        (1, "-", "yamllint", "comments", False),
    ]


def test_run_yamllint_when_clean(tmp_path: Path) -> None:
    """違反の無い YAML（正常系）。"""
    # 準備
    (tmp_path / ".yamllint.yaml").write_text(_YAMLLINT_CONFIG, encoding="utf-8")
    config = load_yamllint_config(tmp_path)
    # 実行
    result = run_yamllint(PurePosixPath("rules.yaml"), "key: value\n", config)
    # 検証
    assert result == []
