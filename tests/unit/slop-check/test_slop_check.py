"""plugins/slop-check/hooks/post-tool-use/slop_check.py の単体テスト。"""

import io
import json
import re
import sys
from typing import TYPE_CHECKING

import pytest

import slop_check
from slop_check import (
    NOTICE_HEAD,
    NOTICE_TAIL,
    Entry,
    build_notice,
    collect_strings,
    compile_entry,
    entry_hits,
    extract_text,
    find_hits,
    is_target,
    is_word_list_write,
    load_entries,
)

if TYPE_CHECKING:
    from pathlib import Path

# 「直す」の 1 行だけを持つ対応表のコピー
_NAOSU_COPY = (
    '{"entries": [{"id": "naosu", "ng": "直す", "ok": ["修正"], '
    '"pattern": "(?<![㐀-鿿々])直(?:さ|し|す|せ|そ|っ)"}]}\n'
)


def _set_stdin(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    """標準入力を、渡した文字列を UTF-8 で読むストリームに差し替える。"""
    monkeypatch.setattr(
        sys, "stdin", io.TextIOWrapper(io.BytesIO(text.encode("utf-8")), encoding="utf-8")
    )


def test_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """ヒットを通知する（正常系）。"""
    # 準備
    word_list = tmp_path / "word-list-ai-slop.json"
    word_list.write_text(_NAOSU_COPY, encoding="utf-8")
    _set_stdin(
        monkeypatch,
        '{"tool_name": "Write", "tool_input": {"file_path": "/r/a.md", "content": "設定を直す。"}}',
    )
    # 実行
    code = slop_check.main([], word_list=word_list)
    # 検証
    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert "| 直す | 修正 |" in output["hookSpecificOutput"]["additionalContext"]


def test_main_when_no_hit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """ヒットしない（正常系）。"""
    # 準備
    word_list = tmp_path / "word-list-ai-slop.json"
    word_list.write_text(_NAOSU_COPY, encoding="utf-8")
    _set_stdin(
        monkeypatch,
        '{"tool_name": "Write", "tool_input": {"file_path": "/r/a.md", "content": "設定を修正する。"}}',
    )
    # 実行
    code = slop_check.main([], word_list=word_list)
    # 検証
    assert code == 0
    assert capsys.readouterr().out == ""


def test_main_when_input_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """入力が読めない（正常系）。"""
    # 準備
    word_list = tmp_path / "word-list-ai-slop.json"
    word_list.write_text(_NAOSU_COPY, encoding="utf-8")
    _set_stdin(monkeypatch, '{"tool_name": "Write"')
    # 実行
    code = slop_check.main([], word_list=word_list)
    # 検証
    assert code == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "JSON" in captured.err


def test_main_when_word_list_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """対応表が無い（正常系）。"""
    # 準備
    word_list = tmp_path / "missing.json"
    _set_stdin(
        monkeypatch,
        '{"tool_name": "Write", "tool_input": {"file_path": "/r/a.md", "content": "設定を直す。"}}',
    )
    # 実行
    code = slop_check.main([], word_list=word_list)
    # 検証
    assert code == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert str(word_list) in captured.err


def test_main_when_writing_word_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """対応表への書き込み（正常系）。"""
    # 準備
    word_list = tmp_path / "word-list-ai-slop.json"
    word_list.write_text(_NAOSU_COPY, encoding="utf-8")
    _set_stdin(
        monkeypatch,
        '{"tool_name": "Write", "tool_input": '
        '{"file_path": "/repo/docs/word-list/word-list-ai-slop.yaml", "content": "ng: 直す"}}',
    )

    # 対応表を読んだらテストを失敗させる
    def _fail_load(path: Path) -> list[Entry]:
        raise AssertionError(path)

    monkeypatch.setattr(slop_check, "load_entries", _fail_load)
    # 実行
    code = slop_check.main([], word_list=word_list)
    # 検証
    assert code == 0
    assert capsys.readouterr().out == ""


def test_main_when_unexpected_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """想定していない例外（正常系）。"""
    # 準備
    word_list = tmp_path / "word-list-ai-slop.json"
    word_list.write_text(_NAOSU_COPY, encoding="utf-8")
    _set_stdin(
        monkeypatch,
        '{"tool_name": "Write", "tool_input": {"file_path": "/r/a.md", "content": "設定を直す。"}}',
    )

    # ヒットした行の照合を、RuntimeError を送出する関数に差し替える
    def _raise(text: str, entries: object) -> list[Entry]:
        raise RuntimeError(text)

    monkeypatch.setattr(slop_check, "find_hits", _raise)
    # 実行
    code = slop_check.main([], word_list=word_list)
    # 検証
    assert code == 0
    assert "Traceback" in capsys.readouterr().err


@pytest.mark.parametrize(
    "tool_name",
    [
        pytest.param("Write", id="write"),
        pytest.param("mcp__plugin_dev-docs_dev-docs__write_docs", id="write_docs"),
        pytest.param("mcp__plugin_ai-monitor_ai-monitor-tools__comment", id="comment"),
        pytest.param("mcp__plugin_mindstella_mindstella__reply", id="mindstella_reply"),
    ],
)
def test_is_target(tool_name: str) -> None:
    """対象のツール（正常系）。"""
    # 実行
    result = is_target(tool_name)
    # 検証
    assert result is True


@pytest.mark.parametrize(
    "tool_name",
    [
        pytest.param("Read", id="read"),
        pytest.param("mcp__plugin_dev-docs_dev-docs__search_docs", id="search_docs"),
        pytest.param("mcp__other__comment", id="other_server"),
    ],
)
def test_is_target_when_not_target(tool_name: str) -> None:
    """対象外のツール（正常系）。"""
    # 実行
    result = is_target(tool_name)
    # 検証
    assert result is False


@pytest.mark.parametrize(
    ("tool_name", "tool_input"),
    [
        pytest.param(
            "Edit", {"file_path": "C:\\repo\\docs\\word-list\\word-list-ai-slop.yaml"}, id="source"
        ),
        pytest.param(
            "Write",
            {"file_path": "/r/plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json"},
            id="copy",
        ),
        pytest.param(
            "mcp__plugin_dev-docs_dev-docs__write_docs",
            {"operations": [{"id": "word-list-ai-slop"}]},
            id="write_docs",
        ),
    ],
)
def test_is_word_list_write(tool_name: str, tool_input: dict[str, object]) -> None:
    """対応表の正本・コピー・write_docs（正常系）。"""
    # 実行
    result = is_word_list_write(tool_name, tool_input)
    # 検証
    assert result is True


@pytest.mark.parametrize(
    ("tool_name", "tool_input"),
    [
        pytest.param("Write", {"file_path": "/r/docs/rule/a.yaml"}, id="rule"),
        pytest.param(
            "mcp__plugin_dev-docs_dev-docs__write_docs",
            {"operations": [{"id": "word-list-ai-slop"}, {"id": "convention-writing-style"}]},
            id="write_docs_mixed",
        ),
    ],
)
def test_is_word_list_write_when_other(tool_name: str, tool_input: dict[str, object]) -> None:
    """対応表でない書き込む先（正常系）。"""
    # 実行
    result = is_word_list_write(tool_name, tool_input)
    # 検証
    assert result is False


def test_extract_text_when_edit(tmp_path: Path) -> None:
    """Edit はファイル全体（正常系）。"""
    # 準備
    path = tmp_path / "a.md"
    path.write_text("新しい版を出す。\n設定を修正する。", encoding="utf-8")
    # 実行
    result = extract_text("Edit", {"file_path": str(path), "new_string": "設定を修正する。"})
    # 検証
    assert result == "新しい版を出す。\n設定を修正する。"


def test_extract_text_when_edit_unreadable(tmp_path: Path) -> None:
    """Edit でファイルが読めない（正常系）。"""
    # 準備
    path = tmp_path / "missing.md"
    # 実行
    result = extract_text("Edit", {"file_path": str(path), "new_string": "設定を直す。"})
    # 検証
    assert result == "設定を直す。"


def test_extract_text_when_mcp() -> None:
    """MCP ツールは文字列の値を集める（正常系）。"""
    # 準備
    tool_input: dict[str, object] = {
        "source": "knowledge",
        "operations": [{"id": "直す", "set": {"body": "設定を足す。"}}],
    }
    # 実行
    result = extract_text("mcp__plugin_dev-docs_dev-docs__write_docs", tool_input)
    # 検証
    assert result == "設定を足す。"


def test_collect_strings() -> None:
    """入れ子をたどり除くキーを飛ばす（正常系）。"""
    # 準備
    value: dict[str, object] = {
        "format": {"body": "a"},
        "labels": ["b"],
        "issue_id": "c",
        "items": ["d", 1],
    }
    # 実行
    result = collect_strings(value)
    # 検証
    assert result == ["a", "d"]


def test_compile_entry() -> None:
    """pattern の有無（正常系）。"""
    # 準備
    plain = {"id": "a", "ng": "直す", "ok": ["修正"]}
    with_pattern = {
        "id": "b",
        "ng": "形",
        "ok": ["スキーマ", "構造"],
        "pattern": "(?<![㐀-鿿々])形(?![㐀-鿿々])",
        "allow": ["形容"],
        "note": "形状の意味なら「形状」",
    }
    # 実行
    plain_entry = compile_entry(plain)
    pattern_entry = compile_entry(with_pattern)
    # 検証
    assert plain_entry == Entry(
        id="a", ng="直す", ok=("修正",), matcher=re.compile("直す"), allow=(), note=None
    )
    assert pattern_entry == Entry(
        id="b",
        ng="形",
        ok=("スキーマ", "構造"),
        matcher=re.compile("(?<![㐀-鿿々])形(?![㐀-鿿々])"),
        allow=("形容",),
        note="形状の意味なら「形状」",
    )


def test_compile_entry_when_invalid_pattern() -> None:
    """読めない正規表現（異常系）。"""
    # 準備
    row = {"id": "a", "ng": "形", "ok": ["構造"], "pattern": "形("}
    # 実行・検証
    with pytest.raises(re.error, match="missing"):
        compile_entry(row)


def test_load_entries(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """並びを保ち、読めない行を除く（正常系）。"""
    # 準備
    path = tmp_path / "word-list-ai-slop.json"
    path.write_text(
        '{"entries": ['
        '{"id": "naosu", "ng": "直す", "ok": ["修正"]}, '
        '{"id": "katachi", "ng": "形", "ok": ["構造"], "pattern": "形("}, '
        '{"id": "han", "ng": "版", "ok": ["バージョン"]}'
        "]}\n",
        encoding="utf-8",
    )
    # 実行
    result = load_entries(path)
    # 検証
    assert [entry.id for entry in result] == ["naosu", "han"]
    assert "katachi" in capsys.readouterr().err


def test_load_entries_when_broken(tmp_path: Path) -> None:
    """JSON として読めない（異常系）。"""
    # 準備
    path = tmp_path / "word-list-ai-slop.json"
    path.write_text("{", encoding="utf-8")
    # 実行・検証
    with pytest.raises(ValueError, match="Expecting"):
        load_entries(path)


def test_entry_hits() -> None:
    """ヒットする（正常系）。"""
    # 準備
    entry = compile_entry(
        {"id": "ateru", "ng": "当てる", "ok": ["適用"], "pattern": "(?<![㐀-鿿々])当て(?:る|た|て)"}
    )
    # 実行
    result = entry_hits("値を当てる。", entry)
    # 検証
    assert result is True


def test_entry_hits_when_allowed() -> None:
    """allow に当たるヒットを除く（正常系）。"""
    # 準備
    entry = compile_entry(
        {
            "id": "ateru",
            "ng": "当てる",
            "ok": ["適用"],
            "pattern": "(?<![㐀-鿿々])当て(?:る|た|て)",
            "allow": ["割り当て"],
        }
    )
    # 実行
    result = entry_hits("設定を割り当てる。", entry)
    # 検証
    assert result is False


def test_entry_hits_when_kanji_around() -> None:
    """前後に漢字が続く漢字 1 文字（正常系）。"""
    # 準備
    entry = compile_entry(
        {"id": "katachi", "ng": "形", "ok": ["構造"], "pattern": "(?<![㐀-鿿々])形(?![㐀-鿿々])"}
    )
    # 実行
    result = entry_hits("形式と円形", entry)
    # 検証
    assert result is False


def test_find_hits() -> None:
    """並びの順で 1 行 1 回（正常系）。"""
    # 準備
    entries = [
        compile_entry(
            {"id": "naosu", "ng": "直す", "ok": ["修正"], "pattern": "(?<![㐀-鿿々])直(?:さ|し|す)"}
        ),
        compile_entry(
            {
                "id": "katachi",
                "ng": "形",
                "ok": ["構造"],
                "pattern": "(?<![㐀-鿿々])形(?![㐀-鿿々])",
            }
        ),
        compile_entry(
            {
                "id": "han",
                "ng": "版",
                "ok": ["バージョン"],
                "pattern": "(?<![㐀-鿿々])版(?![㐀-鿿々])",
            }
        ),
    ]
    # 実行
    result = find_hits("この形で直す。もう一度直す。", entries)
    # 検証
    assert [entry.id for entry in result] == ["naosu", "katachi"]


def test_build_notice() -> None:
    """note を括弧で添える（正常系）。"""
    # 準備
    hits = [
        compile_entry(
            {
                "id": "katachi",
                "ng": "形",
                "ok": ["スキーマ", "構造"],
                "pattern": "(?<![㐀-鿿々])形(?![㐀-鿿々])",
                "note": "形状の意味なら「形状」",
            }
        )
    ]
    # 実行
    result = build_notice(hits)
    # 検証
    assert (
        result
        == NOTICE_HEAD + "\n| 形 | スキーマ・構造（形状の意味なら「形状」） |\n" + NOTICE_TAIL
    )
