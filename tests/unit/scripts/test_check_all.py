"""scripts/check_all.py の単体テスト。"""

import re
from collections.abc import Callable, Mapping
from pathlib import Path, PurePosixPath

import check_all
import pytest
from _lint import LintFinding, LintSource
from check_all import (
    MetaSchemaError,
    Target,
    build_validators,
    check_lints,
    check_target,
    list_targets,
)
from jsonschema import Draft202012Validator

# リポジトリの直下
_REPO = Path(__file__).resolve().parents[3]

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


def _meta() -> Draft202012Validator:
    """リポジトリの拡張したメタスキーマの検査器を返す。"""
    return check_all.load_meta_validator(_REPO)


def _find_clis(_lint_dir: Path) -> dict[str, str | None]:
    """lint の CLI の在りかの確認の差し替え。両方とも引けたパスを返す。"""
    return dict(_CLIS)


def _no_lints(*_args: object) -> list[LintFinding]:
    """lint の検査の差し替え。違反を返さない。"""
    return []


def _lints_returning(findings: list[LintFinding]) -> Callable[..., list[LintFinding]]:
    """lint の検査の差し替え。渡した違反を返す関数を返す。"""

    def _check(*_args: object) -> list[LintFinding]:
        return findings

    return _check


# scripts/lint/.yamllint.yaml と同じ内容の設定
_YAMLLINT_CONFIG = (
    "extends: default\n"
    "rules:\n"
    "  comments:\n"
    "    level: error\n"
    "  document-start: disable\n"
    "  line-length: disable\n"
    "  truthy:\n"
    "    check-keys: false\n"
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
    monkeypatch.setattr(check_all, "find_lint_clis", _find_clis)
    monkeypatch.setattr(check_all, "check_lints", _no_lints)
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
    monkeypatch.setattr(check_all, "find_lint_clis", _find_clis)
    monkeypatch.setattr(check_all, "check_lints", _no_lints)
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
    monkeypatch.setattr(check_all, "find_lint_clis", _find_clis)
    monkeypatch.setattr(
        check_all, "check_lints", _lints_returning([_ERROR_FINDING, _WARNING_FINDING])
    )
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
    monkeypatch.setattr(check_all, "find_lint_clis", _find_clis)
    monkeypatch.setattr(check_all, "check_lints", _lints_returning([_WARNING_FINDING]))
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
    monkeypatch.setattr(check_all, "find_lint_clis", _find_clis)
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


def _first_source_md036(sources: list[LintSource], *_args: object) -> list[LintFinding]:
    """Markdown の lint の呼び出しの差し替え。1 件目の Markdown に MD036 の違反を返す。"""
    return [
        LintFinding(
            sources[0].path, 11, sources[0].item_path, "markdownlint", "MD036", "太字", False
        )
    ]


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
        _first_source_md036,
    )
    # 実行
    result = check_lints(root, [target], texts, lint_dir, _CLIS)
    # 検証
    assert [(str(f.path), f.tool, f.rule) for f in result] == [
        ("docs/rule/rule-a.yaml", "markdownlint", "MD036"),
        ("rules.yaml", "yamllint", "comments"),
        ("rules.yaml", "yamllint", "comments"),
    ]


# 設計書のスキーマが $ref で指す共通の型
_DESIGN_COMMON = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 共通\n"
    "$defs:\n"
    "  id:\n"
    "    type: string\n"
    "    pattern: ^[A-Z]+-\\d+$\n"
)

# 共通の型を $ref で指し、合う examples を持つ設計書のスキーマ
_DESIGN_SCENARIO = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: シナリオ\n"
    "type: object\n"
    "required:\n"
    "  - id\n"
    "properties:\n"
    "  id:\n"
    "    $ref: common.schema.yaml#/$defs/id\n"
    "examples:\n"
    "  - id: SC-1\n"
)

# required の id を持たない examples[0] を持つ設計書のスキーマ（10 行目が要素）
_DESIGN_BAD_EXAMPLE = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: シナリオ\n"
    "type: object\n"
    "required:\n"
    "  - id\n"
    "properties:\n"
    "  id:\n"
    "    $ref: common.schema.yaml#/$defs/id\n"
    "examples:\n"
    "  - title: x\n"
)

# 共通の型に無い $defs を指す設計書のスキーマ（5 行目が $ref）
_DESIGN_BAD_REF = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 参照\n"
    "properties:\n"
    "  id:\n"
    "    $ref: common.schema.yaml#/$defs/missing\n"
)

# type に無い型の名前を書いた設計書のスキーマ（3 行目が type）
_DESIGN_BAD_TYPE = "$schema: https://json-schema.org/draft/2020-12/schema\ntitle: 型\ntype: strin\n"


def test_check_design_schemas(repo_factory: RepoFactory) -> None:
    """誤りの無いスキーマ（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/common.schema.yaml": _DESIGN_COMMON,
            "schemas/design/scenario.schema.yaml": _DESIGN_SCENARIO,
        }
    )
    # 実行
    result = check_all.check_design_schemas(root, _meta())
    # 検証
    assert result == []


def test_check_design_schemas_when_invalid(repo_factory: RepoFactory) -> None:
    """3 種の誤り（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/common.schema.yaml": _DESIGN_COMMON,
            "schemas/design/bad-example.schema.yaml": _DESIGN_BAD_EXAMPLE,
            "schemas/design/bad-ref.schema.yaml": _DESIGN_BAD_REF,
            "schemas/design/bad-type.schema.yaml": _DESIGN_BAD_TYPE,
        }
    )
    # 実行
    result = check_all.check_design_schemas(root, _meta())
    # 検証
    assert len(result) == 3
    assert result[0][:3] == ("schemas/design/bad-example.schema.yaml", 10, "examples[0]")
    assert result[0][3].startswith("examples: ")
    assert result[1][:3] == ("schemas/design/bad-ref.schema.yaml", 5, "properties.id.$ref")
    assert result[1][3].startswith("$ref: common.schema.yaml#/$defs/missing ")
    assert result[2][:3] == ("schemas/design/bad-type.schema.yaml", 3, "type")
    assert result[2][3].startswith("metaschema: ")


def test_check_design_schemas_when_nested_examples(repo_factory: RepoFactory) -> None:
    """入れ子の examples（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/common.schema.yaml": _DESIGN_COMMON,
            "schemas/design/scenario.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: シナリオ\n"
                "properties:\n"
                "  id:\n"
                "    $ref: common.schema.yaml#/$defs/id\n"
                "    examples:\n"
                "      - sc-1\n"
            ),
        }
    )
    # 実行
    result = check_all.check_design_schemas(root, _meta())
    # 検証
    assert len(result) == 1
    assert result[0][:3] == (
        "schemas/design/scenario.schema.yaml",
        7,
        "properties.id.examples[0]",
    )
    assert result[0][3].startswith("examples: ")


def test_check_design_schemas_when_property_named_default(repo_factory: RepoFactory) -> None:
    """default という名前のプロパティ（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/component.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 部品設計\n"
                "properties:\n"
                "  default:\n"
                "    type: string\n"
                "    examples:\n"
                "      - 1\n"
            ),
        }
    )
    # 実行
    result = check_all.check_design_schemas(root, _meta())
    # 検証
    assert len(result) == 1
    assert result[0][:3] == (
        "schemas/design/component.schema.yaml",
        7,
        "properties.default.examples[0]",
    )
    assert result[0][3].startswith("examples: ")


def test_check_design_schemas_when_folder_missing(repo_factory: RepoFactory) -> None:
    """フォルダが無い（正常系）。"""
    # 準備
    root = repo_factory({})
    # 実行
    result = check_all.check_design_schemas(root, _meta())
    # 検証
    assert result == []


def test_check_design_schemas_when_broken(repo_factory: RepoFactory) -> None:
    """読めない YAML（正常系）。"""
    # 準備
    root = repo_factory({"schemas/design/common.schema.yaml": "title: [\n"})
    # 実行
    result = check_all.check_design_schemas(root, _meta())
    # 検証
    assert len(result) == 1
    assert result[0][0] == "schemas/design/common.schema.yaml"
    assert result[0][2] == "$"
    assert result[0][3].startswith("YAML として読めません: ")


def test_main_when_design_schemas_invalid(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_factory: RepoFactory,
    fake_maid_factory: FakeMaidFactory,
) -> None:
    """設計書のスキーマに誤りがある（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/rule-a.yaml": _VALID_A,
            "docs/rule/rule-b.yaml": _VALID_B,
            "schemas/design/common.schema.yaml": _DESIGN_COMMON,
            "schemas/design/scenario.schema.yaml": _DESIGN_BAD_EXAMPLE,
        }
    )
    monkeypatch.chdir(root)
    maid = fake_maid_factory()
    monkeypatch.setattr(check_all, "find_maid", lambda: maid)
    monkeypatch.setattr(check_all, "find_lint_clis", _find_clis)
    monkeypatch.setattr(check_all, "check_lints", _no_lints)
    # 実行
    code = check_all.main([])
    # 検証
    out = capsys.readouterr().out
    assert code == 1
    assert re.search(
        r"^schemas/design/scenario\.schema\.yaml:10: examples\[0\]: examples: ", out, re.MULTILINE
    )
    assert out.splitlines()[-1] == "2 件の文書を検査し、違反は 1 件、警告は 0 件でした"


# properties の下に文字列の x-rules を持ち、$defs の下に reason の無い x-bad-examples の要素を持つスキーマ
_DESIGN_BAD_X_KEYS = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 決まり\n"
    "properties:\n"
    "  id:\n"
    "    x-rules: 1 件の文字列\n"
    "$defs:\n"
    "  a:\n"
    "    x-bad-examples:\n"
    "      - value: 悪い例\n"
)


def test_check_design_schemas_when_x_keys_invalid(repo_factory: RepoFactory) -> None:
    """x-rules・x-bad-examples の形が違う（正常系）。"""
    # 準備
    root = repo_factory({"schemas/design/bad-x.schema.yaml": _DESIGN_BAD_X_KEYS})
    # 実行
    result = check_all.check_design_schemas(root, _meta())
    # 検証
    assert sorted(item[2] for item in result) == [
        "$defs.a.x-bad-examples[0]",
        "properties.id.x-rules",
    ]
    assert all(item[3].startswith("metaschema: ") for item in result)


def test_check_design_schemas_when_x_keys_in_data(repo_factory: RepoFactory) -> None:
    """値の中と同じ名前の項目（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/data.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 値の中\n"
                "properties:\n"
                "  x-rules:\n"
                "    type: string\n"
                "x-bad-examples:\n"
                "  - value:\n"
                "      $ref: missing.schema.yaml\n"
                "      x-rules: 文字列\n"
                "    reason: 理由\n"
            ),
        }
    )
    # 実行
    result = check_all.check_design_schemas(root, _meta())
    # 検証
    assert result == []


def test_load_meta_validator() -> None:
    """正しい拡張したメタスキーマ（正常系）。"""
    # 準備
    invalid = {
        "x-rules": "最上位",
        "properties": {"a": {"x-rules": "properties の下"}},
        "$defs": {"b": {"x-bad-examples": [{"reason": "value が無い"}], "type": "strin"}},
    }
    valid = {
        "properties": {"x-rules": {"type": "string"}},
        "examples": [{"x-rules": "値"}],
        "x-bad-examples": [{"value": {"x-rules": "値"}, "reason": "理由"}],
    }
    # 実行
    validator = check_all.load_meta_validator(_REPO)
    # 検証
    paths = sorted(".".join(map(str, error.absolute_path)) for error in validator.iter_errors(invalid))
    assert paths == [
        "$defs.b.type",
        "$defs.b.x-bad-examples.0",
        "properties.a.x-rules",
        "x-rules",
    ]
    assert list(validator.iter_errors(valid)) == []


def test_load_meta_validator_when_missing(tmp_path: Path) -> None:
    """ファイルが無い（異常系）。"""
    # 実行・検証
    with pytest.raises(MetaSchemaError) as caught:
        check_all.load_meta_validator(tmp_path)
    assert caught.value.message.startswith("schemas/meta.schema.yaml を使えません: ")


def test_load_meta_validator_when_broken(repo_factory: RepoFactory) -> None:
    """読めない YAML（異常系）。"""
    # 準備
    root = repo_factory({"schemas/meta.schema.yaml": "title: [\n"})
    # 実行・検証
    with pytest.raises(MetaSchemaError):
        check_all.load_meta_validator(root)


def test_load_meta_validator_when_invalid(repo_factory: RepoFactory) -> None:
    """メタスキーマに合わない（異常系）。"""
    # 準備
    root = repo_factory({"schemas/meta.schema.yaml": "type: strin\n"})
    # 実行・検証
    with pytest.raises(MetaSchemaError):
        check_all.load_meta_validator(root)


def test_check_document_schemas(repo_factory: RepoFactory) -> None:
    """誤りの無いスキーマ（正常系）。"""
    # 準備
    root = repo_factory(
        {"schemas/template.schema.yaml": "title: テンプレート\nx-rules:\n  - 1 文の決まり。\n"}
    )
    # 実行
    result = check_all.check_document_schemas(root, _meta())
    # 検証
    assert result == []


def test_check_document_schemas_when_invalid(repo_factory: RepoFactory) -> None:
    """x-rules の形が違う（正常系）。"""
    # 準備
    root = repo_factory({"schemas/rule.schema.yaml": "title: 規約\nx-rules: 文字列\n"})
    # 実行
    result = check_all.check_document_schemas(root, _meta())
    # 検証
    assert len(result) == 1
    assert result[0][:3] == ("schemas/rule.schema.yaml", 2, "x-rules")
    assert result[0][3].startswith("metaschema: ")


def test_check_document_schemas_when_broken(repo_factory: RepoFactory) -> None:
    """読めない YAML（正常系）。"""
    # 準備
    root = repo_factory({"schemas/rule.schema.yaml": "title: [\n"})
    # 実行
    result = check_all.check_document_schemas(root, _meta())
    # 検証
    assert len(result) == 1
    assert result[0][2] == "$"
    assert result[0][3].startswith("YAML として読めません: ")


def test_main_when_document_schemas_invalid(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_factory: RepoFactory,
    fake_maid_factory: FakeMaidFactory,
) -> None:
    """schemas/ の直下のスキーマに誤りがある（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/rule-a.yaml": _VALID_A,
            "docs/rule/rule-b.yaml": _VALID_B,
            "schemas/template.schema.yaml": "title: テンプレート\nx-rules: 文字列\n",
        }
    )
    monkeypatch.chdir(root)
    maid = fake_maid_factory()
    monkeypatch.setattr(check_all, "find_maid", lambda: maid)
    monkeypatch.setattr(check_all, "find_lint_clis", _find_clis)
    monkeypatch.setattr(check_all, "check_lints", _no_lints)
    # 実行
    code = check_all.main([])
    # 検証
    assert code == 1
    assert re.search(
        r"^schemas/template\.schema\.yaml:2: x-rules: metaschema: ",
        capsys.readouterr().out,
        re.MULTILINE,
    )


def test_main_when_meta_schema_unusable(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_factory: RepoFactory,
    fake_maid_factory: FakeMaidFactory,
) -> None:
    """拡張したメタスキーマが無い（正常系）。"""
    # 準備
    root = repo_factory({})
    (root / "schemas/meta.schema.yaml").unlink()
    monkeypatch.chdir(root)
    maid = fake_maid_factory()
    monkeypatch.setattr(check_all, "find_maid", lambda: maid)
    monkeypatch.setattr(check_all, "find_lint_clis", _find_clis)
    # 実行
    code = check_all.main([])
    # 検証
    assert code == 2
    assert "schemas/meta.schema.yaml" in capsys.readouterr().err
