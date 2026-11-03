"""対応表のコピーの作成（scripts/build_word_list.py）の結合テスト。"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]

# 正本とコピーの置き場所
_SOURCE = Path("docs/word-list/word-list-ai-slop.yaml")
_COPY = Path("plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json")

# 2 行の正本の対応表
_WORD_LIST = (
    "id: word-list-ai-slop\n"
    "kind: word-list\n"
    "name: 対応表\n"
    "description: 対応表の文書\n"
    "rev: 1\n"
    "entries:\n"
    "  - id: naosu\n"
    "    ng: 直す\n"
    "    ok: [修正]\n"
    "    pattern: '直(?:さ|し|す)'\n"
    "    allow: [書き直]\n"
    "    examples:\n"
    "      hit: [直す]\n"
    "      pass: [修正]\n"
    "  - id: katachi\n"
    "    ng: 形\n"
    "    ok: [スキーマ, 構造]\n"
    "    note: 形状の意味なら「形状」\n"
    "    examples:\n"
    "      hit: [形]\n"
    "      pass: [構造]\n"
)


def _repo(root: Path, *, source: bool) -> Path:
    """正本の対応表（source が真のとき）とコピーの置き場所を持つリポジトリの直下を作る。"""
    (root / _COPY).parent.mkdir(parents=True)
    if source:
        (root / _SOURCE).parent.mkdir(parents=True)
        (root / _SOURCE).write_text(_WORD_LIST, encoding="utf-8")
    return root


def test_normal(run_script: RunScript, tmp_path: Path) -> None:
    """正本の対応表の YAML から、フックが読む JSON のコピーを書き出す（正常系）。"""
    # 準備
    root = _repo(tmp_path / "repo", source=True)
    # 実行
    first = run_script("build_word_list", root)
    copied = (root / _COPY).read_bytes()
    second = run_script("build_word_list", root)
    # 検証
    assert first.exit_code == 0
    assert second.exit_code == 0
    entries = json.loads(copied.decode("utf-8"))["entries"]
    assert [entry["id"] for entry in entries] == ["naosu", "katachi"]
    assert all(set(entry) <= {"id", "ng", "ok", "pattern", "allow", "note"} for entry in entries)
    assert entries[0] == {
        "id": "naosu",
        "ng": "直す",
        "ok": ["修正"],
        "pattern": "直(?:さ|し|す)",
        "allow": ["書き直"],
    }
    assert (root / _COPY).read_bytes() == copied


def test_error_when_source_missing(run_script: RunScript, tmp_path: Path) -> None:
    """正本の対応表が無いか YAML として読めなければ、コピーを書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo(tmp_path / "repo", source=False)
    previous = b'{"entries": []}\n'
    (root / _COPY).write_bytes(previous)
    # 実行
    result = run_script("build_word_list", root)
    # 検証
    assert result.exit_code == 2
    assert str(_SOURCE) in result.stderr
    assert (root / _COPY).read_bytes() == previous
