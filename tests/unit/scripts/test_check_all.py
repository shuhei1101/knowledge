"""scripts/check_all.py の単体テスト。"""

import re
from collections.abc import Callable, Mapping
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import check_all
from _lint import LintFinding
from check_all import Target, build_validators, check_lints, check_target, list_targets

if TYPE_CHECKING:
    import pytest

type FakeMaidFactory = Callable[..., str]
type RepoFactory = Callable[[Mapping[str, str]], Path]

# 両方とも引けたときの lint の CLI の在りか
_CLIS = {"markdownlint-cli2": "/bin/markdownlint-cli2", "textlint": "/bin/textlint"}

# 失敗させるルールの違反と、警告にしたルールの違反
_ERROR_FINDING = LintFinding(
    PurePosixPath("docs/rule/rule-a.yaml"),
    8,
    "items[0].body",
    "markdownlint",
    "MD036",
    "Emphasis used instead of a heading",
    False,
)
_WARNING_FINDING = LintFinding(
    PurePosixPath("docs/rule/rule-a.yaml"),
    8,
    "items[0].body",
    "textlint",
    "one-sentence-per-line",
    "1 行に 2 文があります",
    True,
)

# scripts/lint/.yamllint.yaml と同じ内容の設定
_YAMLLINT_CONFIG = (
    "extends: default\n"
    "rules:\n"
    "  comments:\n"
    "    level: error\n"
    "  document-start: disable\n"
    "  line-length: disable\n"
)

# 違反の無い規約の文書
_VALID_A = (
    "id: rule-a\n"
    "kind: rule\n"
    "name: 規約 A\n"
    "description: 説明\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: 本文\n"
)
_VALID_B = (
    "id: rule-b\n"
    "kind: rule\n"
    "name: 規約 B\n"
    "description: 説明\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: '[A](id:rule-a#overview)'\n"
)

# description が無く、項目の ID が重複した文書
_BROKEN_BOTH = (
    "id: rule-c\n"
    "kind: rule\n"
    "name: 規約 C\n"
    "items:\n"
    "  - id: x\n"
    "    name: 一つ目\n"
    "  - id: x\n"
    "    name: 二つ目\n"
)


def test_main(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_factory: RepoFactory,
    fake_maid_factory: FakeMaidFactory,
) -> None:
    """違反の無いリポジトリ（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/rule-a.yaml": _VALID_A, "docs/rule/rule-b.yaml": _VALID_B})
    monkeypatch.chdir(root)
    maid = fake_maid_factory()
    monkeypatch.setattr(check_all, "find_maid", lambda: maid)
    monkeypatch.setattr(check_all, "find_lint_clis", lambda _lint_dir: _CLIS)
    monkeypatch.setattr(check_all, "check_lints", lambda *_args: [])
    # 実行
    code = check_all.main([])
    # 検証
    assert code == 0
    assert (
        capsys.readouterr().out.splitlines()[-1]
        == "2 件の文書を検査し、違反は 0 件、警告は 0 件でした"
    )


def test_main_when_violations(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_factory: RepoFactory,
    fake_maid_factory: FakeMaidFactory,
) -> None:
    """違反がある（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/rule-b.yaml": (
                "id: rule-b\nkind: rule\nname: 規約 B\nitems:\n  - id: overview\n    name: 概要\n"
            ),
            "docs/rule/rule-c.yaml": (
                "id: rule-c\n"
                "kind: rule\n"
                "name: 規約 C\n"
                "description: 説明\n"
                "items:\n"
                "  - id: x\n"
                "    name: 一つ目\n"
                "  - id: x\n"
                "    name: 二つ目\n"
            ),
        }
    )
    monkeypatch.chdir(root)
    maid = fake_maid_factory()
    monkeypatch.setattr(check_all, "find_maid", lambda: maid)
    monkeypatch.setattr(check_all, "find_lint_clis", lambda _lint_dir: _CLIS)
    monkeypatch.setattr(check_all, "check_lints", lambda *_args: [])
    # 実行
    code = check_all.main([])
    # 検証
    out = capsys.readouterr().out
    assert code == 1
    assert re.search(r"^docs/rule/rule-b\.yaml:\d+: \$: schema: ", out, re.MULTILINE)
    assert re.search(r"^docs/rule/rule-c\.yaml:8: items\[1\]\.id: ", out, re.MULTILINE)


def test_main_when_lint_findings(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_factory: RepoFactory,
    fake_maid_factory: FakeMaidFactory,
) -> None:
    """lint の違反と警告（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/rule-a.yaml": _VALID_A, "docs/rule/rule-b.yaml": _VALID_B})
    monkeypatch.chdir(root)
    maid = fake_maid_factory()
    monkeypatch.setattr(check_all, "find_maid", lambda: maid)
    monkeypatch.setattr(check_all, "find_lint_clis", lambda _lint_dir: _CLIS)
    monkeypatch.setattr(check_all, "check_lints", lambda *_args: [_ERROR_FINDING, _WARNING_FINDING])
    # 実行
    code = check_all.main([])
    # 検証
    lines = capsys.readouterr().out.splitlines()
    assert code == 1
    assert (
        "docs/rule/rule-a.yaml:8: items[0].body: markdownlint/MD036: "
        "Emphasis used instead of a heading"
    ) in lines
    assert (
        "docs/rule/rule-a.yaml:8: items[0].body: warning: textlint/one-sentence-per-line: "
        "1 行に 2 文があります"
    ) in lines
    assert lines[-1] == "2 件の文書を検査し、違反は 1 件、警告は 1 件でした"


def test_main_when_only_warnings(
    monkeypatch: pytest.MonkeyPatch,
    repo_factory: RepoFactory,
    fake_maid_factory: FakeMaidFactory,
) -> None:
    """警告だけ（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/rule-a.yaml": _VALID_A, "docs/rule/rule-b.yaml": _VALID_B})
    monkeypatch.chdir(root)
    maid = fake_maid_factory()
    monkeypatch.setattr(check_all, "find_maid", lambda: maid)
    monkeypatch.setattr(check_all, "find_lint_clis", lambda _lint_dir: _CLIS)
    monkeypatch.setattr(check_all, "check_lints", lambda *_args: [_WARNING_FINDING])
    # 実行
    code = check_all.main([])
    # 検証
    assert code == 0


def test_main_when_check_cli_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_factory: RepoFactory,
) -> None:
    """検査の CLI が無い（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/rule-a.yaml": _VALID_A})
    monkeypatch.chdir(root)
    monkeypatch.setattr(check_all, "find_maid", lambda: None)
    # 実行
    code = check_all.main(["--lint-dir", str(tmp_path / "missing")])
    # 検証
    err_lines = capsys.readouterr().err.splitlines()
    assert code == 2
    assert [line.split(" ", 1)[0] for line in err_lines] == [
        "maid",
        "markdownlint-cli2",
        "textlint",
    ]


def test_main_when_config_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fake_maid_factory: FakeMaidFactory,
) -> None:
    """dev-docs.yaml が無い（正常系）。"""
    # 準備
    monkeypatch.chdir(tmp_path)
    maid = fake_maid_factory()
    monkeypatch.setattr(check_all, "find_maid", lambda: maid)
    monkeypatch.setattr(check_all, "find_lint_clis", lambda _lint_dir: _CLIS)
    # 実行
    code = check_all.main([])
    # 検証
    assert code == 2
    assert "dev-docs.yaml" in capsys.readouterr().err


def test_list_targets(tmp_path: Path) -> None:
    """行のパターンで引く（正常系）。"""
    # 準備
    (tmp_path / "docs" / "rule").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "docs" / "rule" / "a.yaml").write_text("id: a\n", encoding="utf-8")
    (tmp_path / "docs" / "rule" / "b.yaml").write_text("id: b\n", encoding="utf-8")
    (tmp_path / "scripts" / "files.yaml").write_text("files: []\n", encoding="utf-8")
    rows = [
        {
            "id": "rule",
            "paths": ["docs/rule/*.yaml"],
            "schema": "schemas/rule.schema.yaml",
            "validators": ["knowledge-checks"],
        },
        {
            "id": "scripts",
            "paths": ["scripts/files.yaml"],
            "schema": "schemas/files.schema.yaml",
            "records": "files",
        },
    ]
    # 実行
    result = list_targets(tmp_path, rows)
    # 検証
    assert result == [
        Target(
            path=PurePosixPath("docs/rule/a.yaml"), schema="schemas/rule.schema.yaml", checks=True
        ),
        Target(
            path=PurePosixPath("docs/rule/b.yaml"), schema="schemas/rule.schema.yaml", checks=True
        ),
        Target(
            path=PurePosixPath("scripts/files.yaml"),
            schema="schemas/files.schema.yaml",
            checks=False,
        ),
    ]


def test_list_targets_when_excluded(tmp_path: Path) -> None:
    """exclude と無効な行（正常系）。"""
    # 準備
    (tmp_path / "docs" / "rule").mkdir(parents=True)
    (tmp_path / "docs" / "guide").mkdir(parents=True)
    (tmp_path / "docs" / "rule" / "index.yaml").write_text("items: []\n", encoding="utf-8")
    (tmp_path / "docs" / "rule" / "a.yaml").write_text("id: a\n", encoding="utf-8")
    (tmp_path / "docs" / "guide" / "g.yaml").write_text("id: g\n", encoding="utf-8")
    rows = [
        {
            "id": "rule",
            "paths": ["docs/rule/*.yaml"],
            "exclude": ["index.yaml"],
            "schema": "schemas/rule.schema.yaml",
        },
        {
            "id": "guide",
            "paths": ["docs/guide/*.yaml"],
            "schema": "schemas/guide.schema.yaml",
            "enabled": False,
        },
    ]
    # 実行
    result = list_targets(tmp_path, rows)
    # 検証
    assert result == [
        Target(
            path=PurePosixPath("docs/rule/a.yaml"), schema="schemas/rule.schema.yaml", checks=False
        )
    ]


def test_build_validators(repo_factory: RepoFactory) -> None:
    """他のスキーマへの $ref を解く（正常系）。"""
    # 準備
    root = repo_factory({})
    # 実行
    result = build_validators(root, ["schemas/rule.schema.yaml"])
    # 検証
    validator = result["schemas/rule.schema.yaml"]
    assert not isinstance(validator, str)
    assert [
        e.message for e in validator.iter_errors({"id": "a", "kind": "rule", "name": "名前"})
    ] == ["'description' is a required property"]


def test_build_validators_when_missing(repo_factory: RepoFactory) -> None:
    """スキーマが無い（正常系）。"""
    # 準備
    root = repo_factory({})
    # 実行
    result = build_validators(root, ["schemas/missing.schema.yaml"])
    # 検証
    assert isinstance(result["schemas/missing.schema.yaml"], str)


def test_check_target(repo_factory: RepoFactory, fake_maid_factory: FakeMaidFactory) -> None:
    """スキーマと文書の違反を並べる（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/rule-c.yaml": _BROKEN_BOTH})
    validator = build_validators(root, ["schemas/rule.schema.yaml"])["schemas/rule.schema.yaml"]
    target = Target(
        path=PurePosixPath("docs/rule/rule-c.yaml"), schema="schemas/rule.schema.yaml", checks=True
    )
    # 実行
    result = check_target(target, _BROKEN_BOTH, validator, root, fake_maid_factory(), {})
    # 検証
    assert len(result) == 2
    assert result[0][2].startswith("schema: ")
    assert result[1][0] == 7
    assert result[1][1] == "items[1].id"
    assert "行目: " not in result[1][2]


def test_check_target_when_no_checks(repo_factory: RepoFactory) -> None:
    """文書の違反の検査を当てない行（正常系）。"""
    # 準備
    text = "id: rule-c\nkind: rule\nname: 規約 C\ndescription: 説明\nitems:\n  - id: x\n  - id: x\n"
    root = repo_factory({})
    validator = build_validators(root, ["schemas/rule.schema.yaml"])["schemas/rule.schema.yaml"]
    target = Target(
        path=PurePosixPath("docs/rule/rule-c.yaml"), schema="schemas/rule.schema.yaml", checks=False
    )
    # 実行
    result = check_target(target, text, validator, root, "maid", {})
    # 検証
    assert result == []


def test_check_target_when_unreadable(repo_factory: RepoFactory) -> None:
    """読めないファイル（正常系）。"""
    # 準備
    root = repo_factory({})
    target = Target(
        path=PurePosixPath("docs/rule/rule-c.yaml"), schema="schemas/rule.schema.yaml", checks=True
    )
    # 実行
    result = check_target(target, None, "スキーマが無い", root, "maid", {})
    # 検証
    assert result == [(1, "$", "ファイルを UTF-8 で読めません")]


def test_check_target_when_broken(repo_factory: RepoFactory) -> None:
    """読めない YAML（正常系）。"""
    # 準備
    root = repo_factory({})
    validator = build_validators(root, ["schemas/rule.schema.yaml"])["schemas/rule.schema.yaml"]
    target = Target(
        path=PurePosixPath("docs/rule/rule-c.yaml"), schema="schemas/rule.schema.yaml", checks=True
    )
    # 実行
    result = check_target(target, "items:\n  - id: a\n    name: [\n", validator, root, "maid", {})
    # 検証
    assert len(result) == 1
    assert result[0][0] >= 3
    assert result[0][1] == "$"
    assert result[0][2].startswith("YAML として読めません: ")


# 1 行の正本の対応表
_WORD_LIST_SOURCE = (
    "id: word-list-ai-slop\n"
    "kind: word-list\n"
    "entries:\n"
    "  - id: han\n"
    "    ng: 版\n"
    "    ok: [バージョン]\n"
)


def test_check_word_list_copy(repo_factory: RepoFactory) -> None:
    """一致する（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/word-list/word-list-ai-slop.yaml": _WORD_LIST_SOURCE,
            "plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json": (
                '{\n  "entries": [\n    {\n      "id": "han",\n      "ng": "版",\n'
                '      "ok": [\n        "バージョン"\n      ]\n    }\n  ]\n}\n'
            ),
        }
    )
    # 実行
    result = check_all.check_word_list_copy(root)
    # 検証
    assert result == []


def test_check_word_list_copy_when_stale(repo_factory: RepoFactory) -> None:
    """一致しない（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/word-list/word-list-ai-slop.yaml": _WORD_LIST_SOURCE,
            "plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json": '{\n  "entries": []\n}\n',
        }
    )
    # 実行
    result = check_all.check_word_list_copy(root)
    # 検証
    assert len(result) == 1
    assert result[0][0] == "plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json"
    assert result[0][1] == 1
    assert result[0][2] == "$"
    assert "build_word_list.py" in result[0][3]


def test_check_lints(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, repo_factory: RepoFactory
) -> None:
    """3 つの lint の違反を並べる（正常系）。"""
    # 準備
    doc = (
        "id: rule-a\n"
        "kind: rule\n"
        "name: 規約 A\n"
        "description: 説明\n"
        "items:\n"
        "  - id: overview\n"
        "    name: 概要\n"
        "    body: |-\n"
        "      本文。\n"
        "\n"
        "      **太字だけの段落**\n"
    )
    root = repo_factory({"docs/rule/rule-a.yaml": doc, "rules.yaml": "key: foo #bar\n"})
    lint_dir = tmp_path / "lint"
    lint_dir.mkdir()
    (lint_dir / ".yamllint.yaml").write_text(_YAMLLINT_CONFIG, encoding="utf-8")
    target = Target(PurePosixPath("docs/rule/rule-a.yaml"), "schemas/rule.schema.yaml", True)
    texts = {root / "docs/rule/rule-a.yaml": doc}
    monkeypatch.setattr(
        check_all,
        "run_markdown_lints",
        lambda sources, *_args: [
            LintFinding(
                sources[0].path, 11, sources[0].item_path, "markdownlint", "MD036", "太字", False
            )
        ],
    )
    # 実行
    result = check_lints(root, [target], texts, lint_dir, _CLIS)
    # 検証
    assert [(str(f.path), f.tool, f.rule) for f in result] == [
        ("docs/rule/rule-a.yaml", "markdownlint", "MD036"),
        ("rules.yaml", "yamllint", "comments"),
        ("rules.yaml", "yamllint", "comments"),
    ]
