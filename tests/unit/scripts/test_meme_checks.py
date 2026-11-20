"""memes/scripts/meme_checks.py の単体テスト。"""

import json
from typing import TYPE_CHECKING

import meme_checks
from meme_checks import check_meme, load_works

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    import pytest

# タグ topic:薬屋 を持つ作品
_WORK_KUSURIYA = (
    "id: kusuriya\n"
    "title: 薬屋のひとりごと\n"
    "type: anime\n"
    "tags:\n"
    "  - name: topic:薬屋\n"
)


def test_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """違反の無いネットミーム（正常系）。"""
    # 準備
    (tmp_path / "works").mkdir()
    monkeypatch.chdir(tmp_path)
    stdin_factory("id: fx\nterm: FX\ntags:\n  - name: topic:用語\n")
    # 実行
    code = meme_checks.main([])
    # 検証
    assert code == 0
    assert json.loads(capsys.readouterr().out) == []


def test_main_when_unexpected_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """想定していない例外（正常系）。"""

    # 準備
    def _raise(*_args: object) -> list[dict[str, str]]:
        raise RuntimeError("壊れた")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(meme_checks, "check_meme", _raise)
    stdin_factory("id: fx\n")
    # 実行
    code = meme_checks.main([])
    # 検証
    assert code == 1
    assert "Traceback" in capsys.readouterr().err


def test_check_meme(tmp_path: Path) -> None:
    """違反の無いネットミーム（正常系）。"""
    # 準備
    (tmp_path / "works").mkdir()
    (tmp_path / "works" / "kusuriya.yaml").write_text(_WORK_KUSURIYA, encoding="utf-8")
    text = (
        "id: kusuriya-dokudesu\n"
        "term: これ、毒です\n"
        "work: kusuriya\n"
        "tags:\n"
        "  - name: topic:薬屋\n"
        "  - name: topic:セリフ\n"
    )
    # 実行
    result = check_meme(text, tmp_path)
    # 検証
    assert result == []


def test_check_meme_when_work_not_found(tmp_path: Path) -> None:
    """指す作品が無い（正常系）。"""
    # 準備
    (tmp_path / "works").mkdir()
    text = "id: a\nterm: あ\nwork: missing-work\ntags:\n  - name: topic:セリフ\n"
    # 実行
    result = check_meme(text, tmp_path)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "work"
    assert result[0]["rule"].startswith("3 行目: ")
    assert "missing-work" in result[0]["rule"]


def test_check_meme_when_tags_violate(tmp_path: Path) -> None:
    """内容の分類のタグが 2 つで、作品のタグが無い（正常系）。"""
    # 準備
    (tmp_path / "works").mkdir()
    (tmp_path / "works" / "kusuriya.yaml").write_text(_WORK_KUSURIYA, encoding="utf-8")
    text = (
        "id: kusuriya-title\n"
        "term: 薬屋のひとりごと\n"
        "work: kusuriya\n"
        "tags:\n"
        "  - name: topic:セリフ\n"
        "  - name: topic:タイトル\n"
    )
    # 実行
    result = check_meme(text, tmp_path)
    # 検証
    assert len(result) == 2
    assert result[0]["path"] == "tags"
    assert "topic:セリフ" in result[0]["rule"]
    assert "topic:タイトル" in result[0]["rule"]
    assert result[1]["path"] == "tags"
    assert "topic:薬屋" in result[1]["rule"]


def test_check_meme_when_no_content_tag(tmp_path: Path) -> None:
    """内容の分類のタグが無い（正常系）。"""
    # 準備
    (tmp_path / "works").mkdir()
    text = "id: dokagui\nterm: ドカ食い\ntags:\n  - name: topic:食事\n"
    # 実行
    result = check_meme(text, tmp_path)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "tags"


def test_check_meme_when_broken(tmp_path: Path) -> None:
    """読み込めない YAML（正常系）。"""
    # 実行
    result = check_meme("term: [\n", tmp_path)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "$"
    assert "行目: YAML として読めません" in result[0]["rule"]


def test_load_works(tmp_path: Path) -> None:
    """作品の ID とタグを集める（正常系）。"""
    # 準備
    (tmp_path / "works").mkdir()
    (tmp_path / "works" / "kusuriya.yaml").write_text(_WORK_KUSURIYA, encoding="utf-8")
    (tmp_path / "works" / "broken.yaml").write_text("id: [\n", encoding="utf-8")
    # 実行
    result = load_works(tmp_path)
    # 検証
    assert result == {"kusuriya": ("topic:薬屋",)}


def test_load_works_when_missing_dir(tmp_path: Path) -> None:
    """作品のフォルダが無い（正常系）。"""
    # 実行
    result = load_works(tmp_path)
    # 検証
    assert result == {}
