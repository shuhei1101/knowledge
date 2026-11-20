"""ネットミームの検査（memes/scripts/meme_checks.py）の結合テスト。"""

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]

# ネットミームの検査のスクリプトの置き場所
_MEMES_SCRIPTS = Path(__file__).resolve().parents[3] / "memes" / "scripts"

# タグ topic:薬屋 を持つ作品
_WORK_KUSURIYA = "id: kusuriya\ntitle: 薬屋のひとりごと\ntype: anime\ntags:\n  - name: topic:薬屋\n"


def _source(tmp_path: Path) -> Path:
    """works/kusuriya.yaml を持つネットミームの配信元の直下を作る。"""
    root = tmp_path / "memes"
    (root / "works").mkdir(parents=True)
    (root / "works" / "kusuriya.yaml").write_text(_WORK_KUSURIYA, encoding="utf-8")
    return root


def _hashes(root: Path) -> dict[str, str]:
    """フォルダの配下の全てのファイルのハッシュを返す。"""
    return {
        str(file.relative_to(root)): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in sorted(root.rglob("*"))
        if file.is_file()
    }


def test_normal(run_script: RunScript, tmp_path: Path) -> None:
    """違反の無いネットミームに空の配列を返却する（正常系）。"""
    # 準備
    root = _source(tmp_path)
    before = _hashes(root)
    stdin = (
        "id: kusuriya-dokudesu\n"
        "term: これ、毒です\n"
        "work: kusuriya\n"
        "tags:\n"
        "  - name: topic:薬屋\n"
        "  - name: topic:セリフ\n"
        "  - name: topic:危険\n"
    )
    # 実行
    result = run_script("meme_checks", root, stdin, script_dir=_MEMES_SCRIPTS)
    # 検証
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []
    assert _hashes(root) == before


def test_normal_when_work_not_found(run_script: RunScript, tmp_path: Path) -> None:
    """`work` が実在しない作品を指すネットミームに、`work` の違反 1 件を返却する（正常系）。"""
    # 準備
    root = _source(tmp_path)
    stdin = "id: a\nterm: あ\nwork: missing-work\ntags:\n  - name: topic:セリフ\n"
    # 実行
    result = run_script("meme_checks", root, stdin, script_dir=_MEMES_SCRIPTS)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert len(violations) == 1
    assert violations[0]["path"] == "work"
    assert "missing-work" in violations[0]["rule"]


def test_normal_when_tag_vocabulary_violated(run_script: RunScript, tmp_path: Path) -> None:
    """内容の分類のタグが 2 つで、作品のタグが無いネットミームに、`tags` の違反 2 件を返却する（正常系）。"""
    # 準備
    root = _source(tmp_path)
    stdin = (
        "id: kusuriya-title\n"
        "term: 薬屋のひとりごと\n"
        "work: kusuriya\n"
        "tags:\n"
        "  - name: topic:セリフ\n"
        "  - name: topic:タイトル\n"
    )
    # 実行
    result = run_script("meme_checks", root, stdin, script_dir=_MEMES_SCRIPTS)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert len(violations) == 2
    assert violations[0]["path"] == "tags"
    assert violations[1]["path"] == "tags"
    assert "topic:セリフ" in violations[0]["rule"]
    assert "topic:タイトル" in violations[0]["rule"]
    assert "topic:薬屋" in violations[1]["rule"]


def test_normal_when_invalid_yaml(run_script: RunScript, tmp_path: Path) -> None:
    """読み込めない入力を `path: $` の違反 1 件で返却する（正常系）。"""
    # 準備
    root = _source(tmp_path)
    # 実行
    result = run_script("meme_checks", root, "term: [\n", script_dir=_MEMES_SCRIPTS)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert len(violations) == 1
    assert violations[0]["path"] == "$"
