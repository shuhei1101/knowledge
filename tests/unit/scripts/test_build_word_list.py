"""scripts/build_word_list.py の単体テスト。"""

from typing import TYPE_CHECKING

from _common import load_document
from build_word_list import main, render_copy

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# 2 行の正本の対応表
_SOURCE = (
    "id: word-list-ai-slop\n"
    "kind: word-list\n"
    "entries:\n"
    "  - id: naosu\n"
    "    ng: 直す\n"
    "    ok: [修正]\n"
    "    pattern: '直(?:す|し)'\n"
    "    examples:\n"
    "      hit: [直す]\n"
    "      pass: [直接]\n"
    "  - id: han\n"
    "    ng: 版\n"
    "    ok: [バージョン]\n"
)

# _SOURCE から作ったコピー
_COPY = (
    "{\n"
    '  "entries": [\n'
    "    {\n"
    '      "id": "naosu",\n'
    '      "ng": "直す",\n'
    '      "ok": [\n'
    '        "修正"\n'
    "      ],\n"
    '      "pattern": "直(?:す|し)"\n'
    "    },\n"
    "    {\n"
    '      "id": "han",\n'
    '      "ng": "版",\n'
    '      "ok": [\n'
    '        "バージョン"\n'
    "      ]\n"
    "    }\n"
    "  ]\n"
    "}\n"
)


def test_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """コピーを書き出す（正常系）。"""
    # 準備
    (tmp_path / "docs" / "word-list").mkdir(parents=True)
    (tmp_path / "docs" / "word-list" / "word-list-ai-slop.yaml").write_text(
        _SOURCE, encoding="utf-8"
    )
    (tmp_path / "plugins" / "slop-check" / "hooks" / "post-tool-use").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    # 実行
    code = main([])
    # 検証
    assert code == 0
    copy = (
        tmp_path / "plugins" / "slop-check" / "hooks" / "post-tool-use" / "word-list-ai-slop.json"
    )
    assert copy.read_text(encoding="utf-8") == _COPY


def test_main_when_source_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """正本が無い（正常系）。"""
    # 準備
    folder = tmp_path / "plugins" / "slop-check" / "hooks" / "post-tool-use"
    folder.mkdir(parents=True)
    (folder / "word-list-ai-slop.json").write_text('{"entries": []}\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    # 実行
    code = main([])
    # 検証
    assert code == 2
    assert "docs/word-list/word-list-ai-slop.yaml" in capsys.readouterr().err
    assert (folder / "word-list-ai-slop.json").read_text(encoding="utf-8") == '{"entries": []}\n'


def test_render_copy() -> None:
    """残すキーだけを固定の順で（正常系）。"""
    # 準備
    doc = load_document(
        "entries:\n"
        "  - note: 形状の意味なら「形状」\n"
        "    ng: 形\n"
        "    id: katachi\n"
        "    ok: [構造]\n"
        "    allow: [形容]\n"
        "    pattern: 形\n"
        "    examples:\n"
        "      hit: [形]\n"
        "      pass: [形式]\n"
        "  - id: han\n"
        "    ng: 版\n"
        "    ok: [バージョン]\n"
    )
    # 実行
    result = render_copy(doc)
    # 検証
    assert result == (
        "{\n"
        '  "entries": [\n'
        "    {\n"
        '      "id": "katachi",\n'
        '      "ng": "形",\n'
        '      "ok": [\n'
        '        "構造"\n'
        "      ],\n"
        '      "pattern": "形",\n'
        '      "allow": [\n'
        '        "形容"\n'
        "      ],\n"
        '      "note": "形状の意味なら「形状」"\n'
        "    },\n"
        "    {\n"
        '      "id": "han",\n'
        '      "ng": "版",\n'
        '      "ok": [\n'
        '        "バージョン"\n'
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
    )
