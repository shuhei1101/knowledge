"""SKILL.md の生成（scripts/build_skills.py）の結合テスト。"""

import shutil
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]

# リポジトリの設計書のスキーマのフォルダ
_SCHEMAS = Path(__file__).resolve().parents[3] / "schemas" / "design"

# SKILL.md がまだ無い skill の設計書。引数・allowed_tools と、when と calls を持つ工程・持たない工程を持つ
_A_DOC = (
    "id: a\n"
    "type: skill\n"
    "title: A を処理する\n"
    "summary: A を処理するスキル\n"
    "skill:\n"
    "  path: skills/a/SKILL.md\n"
    "  arguments:\n"
    "    - name: range\n"
    "      hint: <範囲>\n"
    "      description: 処理する範囲\n"
    "  allowed_tools:\n"
    "    - Bash(git diff *)\n"
    "steps:\n"
    "  - name: 展開する\n"
    "    when: 範囲があるとき\n"
    "    body: $range をファイルに展開する。\n"
    "    calls:\n"
    "      - type: command\n"
    "        command: git diff --name-only\n"
    "      - type: tool\n"
    "        tool: Read\n"
    "  - name: 終える\n"
    "    body: 終える。\n"
)

# _A_DOC から生成した SKILL.md
_A_SKILL = (
    "---\n"
    "name: a\n"
    "description: A を処理するスキル\n"
    "argument-hint: <範囲>\n"
    "arguments:\n"
    "- range\n"
    "allowed-tools:\n"
    "- Bash(git diff *)\n"
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
    "| `$range` | 処理する範囲 |\n"
    "\n"
    "## 手順\n"
    "\n"
    "### 展開する\n"
    "\n"
    "範囲があるときだけ行う。\n"
    "\n"
    "$range をファイルに展開する。\n"
    "\n"
    "呼ぶもの:\n"
    "\n"
    "- コマンド `git diff --name-only`\n"
    "- ツール `Read`\n"
    "\n"
    "### 終える\n"
    "\n"
    "終える。\n"
)

# 2 つ目の工程を b の「取得する」の埋め込みにした _A_DOC
_A_DOC_WITH_REF = _A_DOC.replace(
    "  - name: 終える\n    body: 終える。\n", "  - name: 終える\n    ref: b#steps[取得する]\n"
)

# 2 つ目の工程を b に無い工程の埋め込みにした _A_DOC
_A_DOC_WITH_MISSING_REF = _A_DOC.replace(
    "  - name: 終える\n    body: 終える。\n", "  - name: 終える\n    ref: b#steps[無い工程]\n"
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
    "    when: 必要なとき\n"
    "    body: B を取得する。\n"
    "    calls:\n"
    "      - type: tool\n"
    "        tool: Read\n"
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
    "必要なときだけ行う。\n"
    "\n"
    "B を取得する。\n"
    "\n"
    "呼ぶもの:\n"
    "\n"
    "- ツール `Read`\n"
)

# skill.path を skill.name に置き換えた _B_DOC
_B_DOC_WITHOUT_PATH = _B_DOC.replace("  path: skills/b/SKILL.md\n", "  name: b\n")

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


def _repo(tmp_path: Path, docs: Mapping[str, str]) -> Path:
    """agent_flow と common のスキーマ・docs/skill/ の設計書・生成済みの b の SKILL.md を持つ一時フォルダを作る。"""
    root = tmp_path / "repo"
    (root / "schemas" / "design").mkdir(parents=True)
    for name in ("agent_flow.schema.yaml", "common.schema.yaml"):
        shutil.copyfile(_SCHEMAS / name, root / "schemas" / "design" / name)
    for name, text in docs.items():
        path = root / "docs" / "skill" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    skill = root / "skills" / "b" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_bytes(_B_SKILL.encode("utf-8"))
    return root


def test_normal(run_script: RunScript, tmp_path: Path) -> None:
    """組み立てた中身が今の SKILL.md と違う設計書だけ、SKILL.md を書き出す（正常系）。"""
    # 準備
    root = _repo(tmp_path, {"a.yaml": _A_DOC, "b.yaml": _B_DOC, "c.yaml": _C_DOC})
    # 実行
    first = run_script("build_skills", root)
    second = run_script("build_skills", root)
    # 検証
    assert first.exit_code == 0, first.stderr
    assert first.stdout == "skills/a/SKILL.md\n"
    assert (root / "skills/a/SKILL.md").read_bytes() == _A_SKILL.encode("utf-8")
    assert (root / "skills/b/SKILL.md").read_bytes() == _B_SKILL.encode("utf-8")
    assert not (root / "skills/c").exists()
    assert second.exit_code == 0
    assert second.stdout == ""
    assert (root / "skills/a/SKILL.md").read_bytes() == _A_SKILL.encode("utf-8")


def test_normal_when_step_ref(run_script: RunScript, tmp_path: Path) -> None:
    """ref を持つ工程は、参照先の工程の中身に置き換えて書き出す（正常系）。"""
    # 準備
    root = _repo(tmp_path, {"a.yaml": _A_DOC_WITH_REF, "b.yaml": _B_DOC, "c.yaml": _C_DOC})
    # 実行
    result = run_script("build_skills", root)
    # 検証
    assert result.exit_code == 0, result.stderr
    text = (root / "skills/a/SKILL.md").read_text(encoding="utf-8")
    assert text.endswith(
        "### 取得する\n\n必要なときだけ行う。\n\nB を取得する。\n\n呼ぶもの:\n\n- ツール `Read`\n"
    )
    assert "### 終える" not in text


def test_error_when_schema_invalid(run_script: RunScript, tmp_path: Path) -> None:
    """スキーマに合わない設計書があれば、どの SKILL.md も書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo(tmp_path, {"a.yaml": _A_DOC, "b.yaml": _B_DOC_WITHOUT_PATH, "c.yaml": _C_DOC})
    # 実行
    result = run_script("build_skills", root)
    # 検証
    assert result.exit_code == 2
    assert "docs/skill/b.yaml" in result.stderr
    assert "skill.path" in result.stderr
    assert not (root / "skills/a/SKILL.md").exists()
    assert (root / "skills/b/SKILL.md").read_bytes() == _B_SKILL.encode("utf-8")


def test_error_when_doc_unreadable(run_script: RunScript, tmp_path: Path) -> None:
    """YAML として読み込めない設計書があれば、どの SKILL.md も書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo(
        tmp_path, {"a.yaml": _A_DOC, "b.yaml": _B_DOC, "c.yaml": 'id: c\nsummary: "閉じていない\n'}
    )
    # 実行
    result = run_script("build_skills", root)
    # 検証
    assert result.exit_code == 2
    assert "docs/skill/c.yaml" in result.stderr
    assert not (root / "skills/a/SKILL.md").exists()
    assert (root / "skills/b/SKILL.md").read_bytes() == _B_SKILL.encode("utf-8")


def test_error_when_step_ref_missing(run_script: RunScript, tmp_path: Path) -> None:
    """ref が指す工程が無ければ、どの SKILL.md も書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo(tmp_path, {"a.yaml": _A_DOC_WITH_MISSING_REF, "b.yaml": _B_DOC, "c.yaml": _C_DOC})
    # 実行
    result = run_script("build_skills", root)
    # 検証
    assert result.exit_code == 2
    assert "docs/skill/a.yaml" in result.stderr
    assert "b#steps[無い工程]" in result.stderr
    assert not (root / "skills/a/SKILL.md").exists()
