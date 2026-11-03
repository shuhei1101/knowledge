"""書き込んだ中身の照合（plugins/slop-check/hooks/post-tool-use/slop_check.py）の結合テスト。"""

import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunHook = Callable[[str, Path], Any]
type PluginFactory = Callable[[Sequence[Mapping[str, object]]], Path]

# 対応表の行
_NAOSU = {
    "id": "naosu",
    "ng": "直す",
    "ok": ["修正"],
    "pattern": "(?<![㐀-鿿々])直(?:さ|し|す|せ|そ|っ)",
}
_TASU = {
    "id": "tasu",
    "ng": "足す",
    "ok": ["追加"],
    "pattern": "(?<![㐀-鿿々])足(?:さ|し|す|せ|そ)",
}
_KATACHI = {
    "id": "katachi",
    "ng": "形",
    "ok": ["スキーマ", "構造"],
    "pattern": "(?<![㐀-鿿々])形(?![㐀-鿿々])",
    "note": "形状の意味なら「形状」",
}
_BAN = {"id": "ban", "ng": "版", "ok": ["バージョン"], "pattern": "(?<![㐀-鿿々])版(?![㐀-鿿々])"}
_ATERU = {"id": "ateru", "ng": "当てる", "ok": ["適用"], "pattern": "当て", "allow": ["割り当て"]}

# 照合の対象の行をすべて持つ対応表
_ALL = [_NAOSU, _TASU, _KATACHI, _BAN]


def _input(tool_name: str, tool_input: Mapping[str, object]) -> str:
    """PostToolUse の入力の JSON を作る。"""
    return json.dumps(
        {"hook_event_name": "PostToolUse", "tool_name": tool_name, "tool_input": tool_input},
        ensure_ascii=False,
    )


def _rows(stdout: str) -> list[str]:
    """通知の文の表の行（見出しと区切りを除く）を返す。"""
    context = json.loads(stdout)["hookSpecificOutput"]["additionalContext"]
    return [
        line
        for line in context.splitlines()
        if line.startswith("| ") and line not in {"| NG | OK |", "| --- | --- |"}
    ]


def test_normal(run_hook: RunHook, plugin_factory: PluginFactory) -> None:
    """Write の中身にヒットした単語の行だけの表を持つ通知の文を返す（正常系）。"""
    # 準備
    root = plugin_factory([_NAOSU, _KATACHI, _BAN])
    stdin = _input("Write", {"file_path": "/work/a.md", "content": "この形で直す。もう一度直す。"})
    # 実行
    result = run_hook(stdin, root)
    # 検証
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert _rows(result.stdout) == [
        "| 直す | 修正 |",
        "| 形 | スキーマ・構造（形状の意味なら「形状」） |",
    ]
    assert "decision" not in output


def test_normal_when_no_word_hits(run_hook: RunHook, plugin_factory: PluginFactory) -> None:
    """ヒットが無いか、ヒットが全て allow に当たれば何も出力しない（正常系）。"""
    # 準備
    root = plugin_factory([_ATERU, _KATACHI])
    stdin = _input(
        "Write", {"file_path": "/work/a.md", "content": "設定を割り当てる。形式と円形を確認する。"}
    )
    # 実行
    result = run_hook(stdin, root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout == ""


def test_normal_when_edit(run_hook: RunHook, plugin_factory: PluginFactory, tmp_path: Path) -> None:
    """Edit は修正後のファイル全体を照合し、前からある単語も通知する（正常系）。"""
    # 準備
    root = plugin_factory(_ALL)
    edited = tmp_path / "edited.md"
    edited.write_text("新しい版を出す。\n設定を修正する。\n", encoding="utf-8")
    stdin = _input(
        "Edit",
        {"file_path": str(edited), "old_string": "設定", "new_string": "設定を修正する。"},
    )
    # 実行
    result = run_hook(stdin, root)
    # 検証
    assert result.exit_code == 0
    assert _rows(result.stdout) == ["| 版 | バージョン |"]


def test_normal_when_edited_file_unreadable(
    run_hook: RunHook, plugin_factory: PluginFactory, tmp_path: Path
) -> None:
    """修正後のファイルが読めなければ new_string を照合する（正常系）。"""
    # 準備
    root = plugin_factory(_ALL)
    stdin = _input(
        "Edit",
        {
            "file_path": str(tmp_path / "missing.md"),
            "old_string": "設定",
            "new_string": "設定を直す。",
        },
    )
    # 実行
    result = run_hook(stdin, root)
    # 検証
    assert result.exit_code == 0
    assert _rows(result.stdout) == ["| 直す | 修正 |"]


def test_normal_when_notebook_edit(run_hook: RunHook, plugin_factory: PluginFactory) -> None:
    """NotebookEdit はセルの新しい中身を照合する（正常系）。"""
    # 準備
    root = plugin_factory(_ALL)
    stdin = _input("NotebookEdit", {"notebook_path": "/work/a.ipynb", "new_source": "# 版を出す"})
    # 実行
    result = run_hook(stdin, root)
    # 検証
    assert result.exit_code == 0
    assert _rows(result.stdout) == ["| 版 | バージョン |"]


def test_normal_when_mcp_tool(run_hook: RunHook, plugin_factory: PluginFactory) -> None:
    """対象の MCP ツールは、識別子のキーを除いた全ての文字列の値を照合する（正常系）。"""
    # 準備
    root = plugin_factory(_ALL)
    stdin = _input(
        "mcp__plugin_dev-docs_dev-docs__write_docs",
        {"operations": [{"op": "update", "id": "直す", "set": {"body": "設定を足す。"}}]},
    )
    # 実行
    result = run_hook(stdin, root)
    # 検証
    assert result.exit_code == 0
    assert _rows(result.stdout) == ["| 足す | 追加 |"]


def test_normal_when_tool_not_target(run_hook: RunHook, plugin_factory: PluginFactory) -> None:
    """対象の一覧に無いツールは照合せずに何も出力しない（正常系）。"""
    # 準備
    root = plugin_factory(_ALL)
    stdin = _input("mcp__plugin_dev-docs_dev-docs__search_docs", {"term": "直す"})
    # 実行
    result = run_hook(stdin, root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout == ""


def test_normal_when_writing_word_list(run_hook: RunHook, plugin_factory: PluginFactory) -> None:
    """対応表の正本とコピーへの書き込みは照合せずに何も出力しない（正常系）。"""
    # 準備
    root = plugin_factory(_ALL)
    stdin = _input(
        "Write",
        {"file_path": "/repo/docs/word-list/word-list-ai-slop.yaml", "content": "ng: 直す"},
    )
    # 実行
    result = run_hook(stdin, root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout == ""


def test_error_when_word_list_missing(run_hook: RunHook, tmp_path: Path) -> None:
    """対応表のコピーが無いか JSON として読めなければ、何も出力せずに理由を標準エラーへ出す（異常系）。"""
    # 準備
    root = tmp_path / "empty-plugin"
    root.mkdir()
    stdin = _input("Write", {"file_path": "/work/a.md", "content": "設定を直す。"})
    # 実行
    result = run_hook(stdin, root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout == ""
    assert str(root / "hooks" / "post-tool-use" / "word-list-ai-slop.json") in result.stderr


def test_error_when_input_invalid(run_hook: RunHook, plugin_factory: PluginFactory) -> None:
    """標準入力が JSON として読めなければ、何も出力せずに理由を標準エラーへ出す（異常系）。"""
    # 準備
    root = plugin_factory(_ALL)
    # 実行
    result = run_hook('{"tool_name": "Write"', root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout == ""
    assert "JSON" in result.stderr
