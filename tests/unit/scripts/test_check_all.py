"""scripts/check_all.py の単体テスト。"""

import re
from collections.abc import Callable, Mapping
from pathlib import Path, PurePosixPath

import pytest

import check_all
from check_all import ConfigError, Target, build_validators, check_target, list_targets, load_config

type FakeMaidFactory = Callable[..., str]
type RepoFactory = Callable[[Mapping[str, str]], Path]

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
    # 実行
    code = check_all.main([])
    # 検証
    assert code == 0
    assert capsys.readouterr().out.splitlines()[-1] == "2 件の文書を検査し、違反は 0 件でした"


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
    # 実行
    code = check_all.main([])
    # 検証
    out = capsys.readouterr().out
    assert code == 1
    assert re.search(r"^docs/rule/rule-b\.yaml:\d+: \$: schema: ", out, re.MULTILINE)
    assert re.search(r"^docs/rule/rule-c\.yaml:8: items\[1\]\.id: ", out, re.MULTILINE)


def test_main_when_maid_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_factory: RepoFactory,
) -> None:
    """maid が無い（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/rule-a.yaml": _VALID_A})
    monkeypatch.chdir(root)
    monkeypatch.setattr(check_all, "find_maid", lambda: None)
    # 実行
    code = check_all.main([])
    # 検証
    assert code == 2
    assert "maid" in capsys.readouterr().err


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
    # 実行
    code = check_all.main([])
    # 検証
    assert code == 2
    assert "dev-docs.yaml" in capsys.readouterr().err


def test_load_config(tmp_path: Path) -> None:
    """行を読む（正常系）。"""
    # 準備
    (tmp_path / "dev-docs.yaml").write_text(
        "name: knowledge\n"
        "documents:\n"
        "  - id: rule\n"
        "    paths:\n"
        "      - docs/rule/*.yaml\n"
        "    schema: schemas/rule.schema.yaml\n"
        "  - id: guide\n"
        "    paths:\n"
        "      - docs/guide/*.yaml\n"
        "    schema: schemas/guide.schema.yaml\n",
        encoding="utf-8",
    )
    # 実行
    result = load_config(tmp_path)
    # 検証
    assert len(result) == 2


def test_load_config_when_missing(tmp_path: Path) -> None:
    """ファイルが無い（異常系）。"""
    # 実行・検証
    with pytest.raises(ConfigError, match=r"dev-docs\.yaml がありません"):
        load_config(tmp_path)


def test_load_config_when_broken(tmp_path: Path) -> None:
    """YAML として読めない（異常系）。"""
    # 準備
    (tmp_path / "dev-docs.yaml").write_text("name: knowledge\ndocuments: [\n", encoding="utf-8")
    # 実行・検証
    with pytest.raises(ConfigError, match=r"dev-docs\.yaml の \d+ 行目が読めません"):
        load_config(tmp_path)


def test_load_config_when_no_documents(tmp_path: Path) -> None:
    """documents が無い（異常系）。"""
    # 準備
    (tmp_path / "dev-docs.yaml").write_text("name: knowledge\n", encoding="utf-8")
    # 実行・検証
    with pytest.raises(ConfigError, match=r"dev-docs\.yaml に documents の配列がありません"):
        load_config(tmp_path)


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
