"""scripts/build_skills.py の単体テスト。"""

import shutil
from pathlib import Path, PurePosixPath

import pytest
from build_skills import (
    SkillPlan,
    load_skill_docs,
    main,
    plan_skills,
    render_call,
    render_frontmatter,
    render_skill,
    render_step,
    resolve_steps,
    write_skill,
)
from build_templates import BuildError

from _common import load_safe

# リポジトリの設計書のスキーマのフォルダ
_SCHEMAS = Path(__file__).resolve().parents[3] / "schemas" / "design"

# SKILL.md がまだ無い skill の設計書
_A_DOC = (
    "id: a\n"
    "type: skill\n"
    "title: A を処理する\n"
    "summary: A を処理するスキル\n"
    "skill:\n"
    "  path: skills/a/SKILL.md\n"
    "steps:\n"
    "  - name: 処理する\n"
    "    body: A を処理する。\n"
)

# 生成済みの skill の設計書
_B_DOC = (
    "id: b\n"
    "type: skill\n"
    "title: B を処理する\n"
    "summary: B を処理するスキル\n"
    "skill:\n"
    "  path: skills/b/SKILL.md\n"
    "steps:\n"
    "  - name: 取得する\n"
    "    body: B を取得する。\n"
)

# _B_DOC から生成した SKILL.md
_B_SKILL = (
    "---\n"
    "name: b\n"
    "description: B を処理するスキル\n"
    "---\n"
    "\n"
    "<!-- docs/skill/b.yaml から生成した。このファイルを修正せず、設計書を修正して再生成する -->\n"
    "\n"
    "# B を処理する\n"
    "\n"
    "## 手順\n"
    "\n"
    "### 取得する\n"
    "\n"
    "B を取得する。\n"
)

# skill.path が無い skill の設計書
_B_DOC_WITHOUT_PATH = (
    "id: b\n"
    "type: skill\n"
    "summary: B を処理するスキル\n"
    "skill:\n"
    "  name: b\n"
    "steps:\n"
    "  - name: 取得する\n"
    "    body: B を取得する。\n"
)

# skill.path がリポジトリの外を指す skill の設計書
_B_DOC_OUTSIDE = (
    "id: b\n"
    "type: skill\n"
    "title: B を処理する\n"
    "summary: B を処理するスキル\n"
    "skill:\n"
    "  path: ../out/SKILL.md\n"
    "steps:\n"
    "  - name: 取得する\n"
    "    body: B を取得する。\n"
)

# flow の設計書
_C_DOC = (
    "id: c\n"
    "type: flow\n"
    "summary: C の流れ\n"
    "condition: C を実行するとき\n"
    "steps:\n"
    "  - name: 実行する\n"
    "    body: C を実行する。\n"
)


def _repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """schemas/design/ のコピーと、指定したファイルを持つリポジトリの直下を作る。"""
    root = tmp_path / "repo"
    shutil.copytree(_SCHEMAS, root / "schemas" / "design")
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def test_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """違うものだけ書き出す（正常系）。"""
    # 準備
    root = _repo(
        tmp_path,
        {
            "docs/skill/a.yaml": _A_DOC,
            "docs/skill/b.yaml": _B_DOC,
            "skills/b/SKILL.md": _B_SKILL,
        },
    )
    monkeypatch.chdir(root)
    # 実行
    code = main([])
    # 検証
    assert code == 0
    assert capsys.readouterr().out == "skills/a/SKILL.md\n"
    assert (root / "skills/a/SKILL.md").is_file()
    assert (root / "skills/b/SKILL.md").read_text(encoding="utf-8") == _B_SKILL


def test_main_when_build_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """生成できない（異常系）。"""
    # 準備
    root = _repo(tmp_path, {"docs/skill/a.yaml": _A_DOC, "docs/skill/b.yaml": _B_DOC_WITHOUT_PATH})
    monkeypatch.chdir(root)
    # 実行
    code = main([])
    # 検証
    assert code == 2
    assert "docs/skill/b.yaml" in capsys.readouterr().err
    assert not (root / "skills").exists()


def test_main_when_unexpected_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """想定していない例外（異常系）。"""
    # 準備
    root = _repo(tmp_path, {"docs/skill/a.yaml": _A_DOC})
    monkeypatch.chdir(root)

    def _raise(_root: Path) -> list[SkillPlan]:
        message = "想定していない例外"
        raise RuntimeError(message)

    monkeypatch.setattr("build_skills.plan_skills", _raise)
    # 実行
    code = main([])
    # 検証
    assert code == 1
    assert "Traceback" in capsys.readouterr().err


def test_plan_skills(tmp_path: Path) -> None:
    """skill だけを組み立てる（正常系）。"""
    # 準備
    root = _repo(tmp_path, {"docs/skill/b.yaml": _B_DOC, "docs/skill/c.yaml": _C_DOC})
    # 実行
    result = plan_skills(root)
    # 検証
    assert result == [SkillPlan(path=PurePosixPath("skills/b/SKILL.md"), text=_B_SKILL)]


def test_plan_skills_when_schema_invalid(tmp_path: Path) -> None:
    """スキーマに合わない設計書（異常系）。"""
    # 準備
    root = _repo(tmp_path, {"docs/skill/b.yaml": _B_DOC_WITHOUT_PATH})
    # 実行・検証
    with pytest.raises(BuildError, match=r"docs/skill/b\.yaml: skill\.path"):
        plan_skills(root)


def test_plan_skills_when_path_outside(tmp_path: Path) -> None:
    """リポジトリの外を指す skill.path（異常系）。"""
    # 準備
    root = _repo(tmp_path, {"docs/skill/b.yaml": _B_DOC_OUTSIDE})
    # 実行・検証
    with pytest.raises(BuildError, match=r"docs/skill/b\.yaml"):
        plan_skills(root)


def test_load_skill_docs_when_unreadable(tmp_path: Path) -> None:
    """YAML として読み込めない（異常系）。"""
    # 準備
    root = _repo(tmp_path, {"docs/skill/c.yaml": 'id: c\nsummary: "閉じていない\n'})
    # 実行・検証
    with pytest.raises(BuildError, match=r"docs/skill/c\.yaml"):
        load_skill_docs(root)


def test_resolve_steps() -> None:
    """ref を参照先に置き換える（正常系）。"""
    # 準備
    docs = {
        PurePosixPath("docs/skill/a.yaml"): {
            "id": "a",
            "steps": [
                {"name": "処理する", "body": "A を処理する。"},
                {"name": "取得する", "ref": "b#steps[取得する]"},
            ],
        },
        PurePosixPath("docs/skill/b.yaml"): {
            "id": "b",
            "steps": [{"name": "取得する", "when": "必要なとき", "body": "B を取得する。"}],
        },
    }
    # 実行
    result = resolve_steps(PurePosixPath("docs/skill/a.yaml"), docs)
    # 検証
    assert result == [
        {"name": "処理する", "body": "A を処理する。"},
        {"name": "取得する", "when": "必要なとき", "body": "B を取得する。"},
    ]


def test_resolve_steps_when_missing() -> None:
    """参照先が無い（異常系）。"""
    # 準備
    docs = {
        PurePosixPath("docs/skill/a.yaml"): {
            "id": "a",
            "steps": [{"name": "取得する", "ref": "b#steps[無い工程]"}],
        },
        PurePosixPath("docs/skill/b.yaml"): {
            "id": "b",
            "steps": [{"name": "取得する", "body": "B を取得する。"}],
        },
    }
    # 実行・検証
    with pytest.raises(BuildError, match=r"b#steps\[無い工程\]"):
        resolve_steps(PurePosixPath("docs/skill/a.yaml"), docs)


def test_resolve_steps_when_cyclic() -> None:
    """戻る ref（異常系）。"""
    # 準備
    docs = {
        PurePosixPath("docs/skill/a.yaml"): {
            "id": "a",
            "steps": [{"name": "取得する", "ref": "b#steps[取得する]"}],
        },
        PurePosixPath("docs/skill/b.yaml"): {
            "id": "b",
            "steps": [{"name": "取得する", "ref": "a#steps[取得する]"}],
        },
    }
    # 実行・検証
    with pytest.raises(BuildError, match=r"docs/skill/a\.yaml"):
        resolve_steps(PurePosixPath("docs/skill/a.yaml"), docs)


def test_render_skill() -> None:
    """引数と工程を持つスキル（正常系）。"""
    # 準備
    doc: dict[str, object] = {
        "id": "a",
        "type": "skill",
        "title": "A を処理する",
        "summary": "A を処理するスキル",
        "skill": {
            "path": "skills/a/SKILL.md",
            "arguments": [{"name": "range", "hint": "<範囲>", "description": "点検する範囲"}],
        },
    }
    steps: list[dict[str, object]] = [
        {"name": "処理する", "body": "$range を処理する。"},
        {"name": "終える", "body": "終える。"},
    ]
    # 実行
    result = render_skill(doc, PurePosixPath("docs/skill/a.yaml"), steps)
    # 検証
    assert result == (
        "---\n"
        "name: a\n"
        "description: A を処理するスキル\n"
        "argument-hint: <範囲>\n"
        "arguments:\n"
        "- range\n"
        "---\n"
        "\n"
        "<!-- docs/skill/a.yaml から生成した。このファイルを修正せず、設計書を修正して再生成する -->\n"
        "\n"
        "# A を処理する\n"
        "\n"
        "## 引数\n"
        "\n"
        "| 引数 | 説明 |\n"
        "| --- | --- |\n"
        "| `$range` | 点検する範囲 |\n"
        "\n"
        "## 手順\n"
        "\n"
        "### 処理する\n"
        "\n"
        "$range を処理する。\n"
        "\n"
        "### 終える\n"
        "\n"
        "終える。\n"
    )


def test_render_skill_when_no_arguments() -> None:
    """引数を持たないスキル（正常系）。"""
    # 準備
    doc: dict[str, object] = {
        "id": "b",
        "type": "skill",
        "title": "B を処理する",
        "summary": "B を処理するスキル",
        "skill": {"path": "skills/b/SKILL.md"},
    }
    steps: list[dict[str, object]] = [{"name": "取得する", "body": "B を取得する。"}]
    # 実行
    result = render_skill(doc, PurePosixPath("docs/skill/b.yaml"), steps)
    # 検証
    assert "## 引数" not in result
    assert result == _B_SKILL


def test_render_frontmatter() -> None:
    """全てのキー（正常系）。"""
    # 準備
    doc: dict[str, object] = {
        "summary": "A を処理するスキル",
        "skill": {
            "path": "skills/a/SKILL.md",
            "arguments": [
                {"name": "range", "hint": "<範囲>", "description": "点検する範囲"},
                {"name": "mode", "hint": "[mode]", "description": "点検の種類"},
            ],
            "allowed_tools": ["Bash(git diff *)"],
            "frontmatter": {"paths": ["docs/**"]},
        },
    }
    # 実行
    result = render_frontmatter(doc)
    # 検証
    assert result.startswith("---\n")
    assert result.endswith("\n---")
    data = load_safe(result.removeprefix("---\n").removesuffix("---"))
    assert data == {
        "name": "a",
        "description": "A を処理するスキル",
        "argument-hint": "<範囲> [mode]",
        "arguments": ["range", "mode"],
        "allowed-tools": ["Bash(git diff *)"],
        "paths": ["docs/**"],
    }
    assert isinstance(data, dict)
    assert list(data) == [  # pyright: ignore[reportUnknownArgumentType]
        "name",
        "description",
        "argument-hint",
        "arguments",
        "allowed-tools",
        "paths",
    ]


def test_render_frontmatter_when_minimal() -> None:
    """任意のキーが無い（正常系）。"""
    # 準備
    doc: dict[str, object] = {
        "summary": "B を処理するスキル",
        "skill": {"path": "skills/b/SKILL.md"},
    }
    # 実行
    result = render_frontmatter(doc)
    # 検証
    assert result == "---\nname: b\ndescription: B を処理するスキル\n---"


def test_render_step() -> None:
    """条件と呼ぶものを持つ工程（正常系）。"""
    # 準備
    step: dict[str, object] = {
        "name": "まとめて修正する",
        "when": "一覧が空でないとき",
        "body": "一覧の箇所を修正する。",
        "calls": [{"type": "tool", "tool": "Edit"}],
    }
    # 実行
    result = render_step(step)
    # 検証
    assert result == (
        "### まとめて修正する\n"
        "\n"
        "一覧が空でないときだけ行う。\n"
        "\n"
        "一覧の箇所を修正する。\n"
        "\n"
        "呼ぶもの:\n"
        "\n"
        "- ツール `Edit`"
    )


def test_render_step_when_body_only() -> None:
    """本文だけの工程（正常系）。"""
    # 準備
    step: dict[str, object] = {"name": "サマリーを出す", "body": "件数を出す。"}
    # 実行
    result = render_step(step)
    # 検証
    assert result == "### サマリーを出す\n\n件数を出す。"


@pytest.mark.parametrize(
    ("call", "expected"),
    [
        pytest.param({"type": "tool", "tool": "Read"}, "- ツール `Read`", id="tool"),
        pytest.param(
            {
                "type": "mcp",
                "server": "MCP-1#",
                "tool": "search_docs",
                "args": {"source": "knowledge"},
            },
            '- MCP `MCP-1#` の `search_docs` `{"source": "knowledge"}`',
            id="mcp",
        ),
        pytest.param(
            {"type": "command", "command": "git diff --name-only"},
            "- コマンド `git diff --name-only`",
            id="command",
        ),
        pytest.param({"type": "skill", "skill": "b#"}, "- スキル `b#`", id="skill"),
        pytest.param({"type": "flow", "flow": "c#"}, "- エージェントフロー `c#`", id="flow"),
        pytest.param(
            {"type": "agent", "instruction": "範囲を調べる"},
            "- サブエージェント `general-purpose`: 範囲を調べる",
            id="agent",
        ),
    ],
)
def test_render_call(call: dict[str, object], expected: str) -> None:
    """種類ごとの書式（正常系）。"""
    # 実行
    result = render_call(call)
    # 検証
    assert result == expected


def test_write_skill(tmp_path: Path) -> None:
    """無いファイルを作り、同じ中身なら書き出さない（正常系）。"""
    # 準備
    plan = SkillPlan(path=PurePosixPath("skills/b/SKILL.md"), text=_B_SKILL)
    # 実行
    first = write_skill(tmp_path, plan)
    second = write_skill(tmp_path, plan)
    # 検証
    assert first is True
    assert second is False
    assert (tmp_path / "skills/b/SKILL.md").read_bytes() == _B_SKILL.encode("utf-8")
