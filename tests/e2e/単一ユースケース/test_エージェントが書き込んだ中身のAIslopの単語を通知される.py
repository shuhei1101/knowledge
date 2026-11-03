"""エージェントが書き込んだ中身の AI slop の単語を通知される（SC-148-1）の E2E テスト。

Claude Code がフックを呼ぶときと同じ PostToolUse の入力を、クローンのプラグインの hooks.json に登録したコマンドへ
標準入力で与えて子プロセスとして起動する。Claude Code の起動とモデルの呼び出しは含めない。
"""

import json
import os
import subprocess
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

# conftest の fixture の型
type KnowledgeClone = Callable[..., Path]

# クローンの中のプラグインのフォルダと、フックが読む対応表のコピー
_PLUGIN = Path("plugins/slop-check")
_WORD_LIST_COPY = _PLUGIN / "hooks" / "post-tool-use" / "word-list-ai-slop.json"
_PLUGIN_ROOT_VARIABLE = "${CLAUDE_PLUGIN_ROOT}"

# 子プロセスを待つ上限の秒数
_WAIT_SEC = 30

# 通知の文の表の見出しと区切りの行
_TABLE_HEAD = {"| NG | OK |", "| --- | --- |"}


def _run_hook(
    clone: Path, tool_name: str, tool_input: Mapping[str, object]
) -> subprocess.CompletedProcess[str]:
    """クローンの hooks.json の PostToolUse のコマンドを、PostToolUse の入力を標準入力に与えて起動する。"""
    plugin_root = clone / _PLUGIN
    hooks = json.loads((plugin_root / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    hook = hooks["hooks"]["PostToolUse"][0]["hooks"][0]
    args = [arg.replace(_PLUGIN_ROOT_VARIABLE, str(plugin_root)) for arg in hook["args"]]
    stdin = json.dumps(
        {"hook_event_name": "PostToolUse", "tool_name": tool_name, "tool_input": tool_input},
        ensure_ascii=False,
    )
    return subprocess.run(  # noqa: S603 - hooks.json のコマンドを配列で渡し、シェルを通さない
        [hook["command"], *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(plugin_root)},
        cwd=clone,
        timeout=_WAIT_SEC,
        check=False,
    )


def _output(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    """フックの標準出力の JSON を返す。"""
    return json.loads(result.stdout)


def _rows(result: subprocess.CompletedProcess[str]) -> list[str]:
    """通知の文の表の行（見出しと区切りを除く）を返す。"""
    context = _output(result)["hookSpecificOutput"]["additionalContext"]
    return [
        line for line in context.splitlines() if line.startswith("| ") and line not in _TABLE_HEAD
    ]


def test_normal(knowledge_clone: KnowledgeClone, tmp_path: Path) -> None:
    """Write の中身にヒットした単語の行だけの表を持つ通知の文が返る（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    content = "設定を直す。この形で記載する。"
    written = tmp_path / "written.md"
    # 実行
    written.write_text(content, encoding="utf-8")
    result = _run_hook(clone, "Write", {"file_path": str(written), "content": content})
    # 検証
    assert written.read_text(encoding="utf-8") == content
    assert result.returncode == 0
    output = _output(result)
    assert "decision" not in output
    assert _rows(result) == ["| 直す | 修正 |", "| 形 | スキーマ・構造（形状の意味なら「形状」） |"]
    context = output["hookSpecificOutput"]["additionalContext"]
    assert '"values": ["convention-writing-style"]' in context
    assert '"values": ["ui-input-wording"]' in context


def test_normal_when_no_word_hits(knowledge_clone: KnowledgeClone, tmp_path: Path) -> None:
    """対応表の単語を含まない中身では何も出力しない（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    content = "設定を修正して割り当てる。形式と円形を確認する。"
    # 実行
    result = _run_hook(
        clone, "Write", {"file_path": str(tmp_path / "written.md"), "content": content}
    )
    # 検証
    assert result.returncode == 0
    assert result.stdout == ""


def test_normal_when_edit_keeps_existing_word(
    knowledge_clone: KnowledgeClone, tmp_path: Path
) -> None:
    """Edit で書き込んだ差分に単語が無くても、ファイルに前からある単語を通知する（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    edited = tmp_path / "edited.md"
    edited.write_text("新しい版を出す。\n設定する。\n", encoding="utf-8")
    # 実行
    edited.write_text("新しい版を出す。\n設定を修正する。\n", encoding="utf-8")
    result = _run_hook(
        clone,
        "Edit",
        {"file_path": str(edited), "old_string": "設定する。", "new_string": "設定を修正する。"},
    )
    # 検証
    assert result.returncode == 0
    assert "decision" not in _output(result)
    assert "| 版 | バージョン |" in _rows(result)


def test_normal_when_mcp_tool_writes(knowledge_clone: KnowledgeClone) -> None:
    """write_docs で書き込む文字列の項目の単語を通知する（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    tool_input = {
        "source": "knowledge",
        "operations": [{"op": "update", "id": "e2e-doc", "set": {"description": "設定を足す。"}}],
    }
    # 実行
    result = _run_hook(clone, "mcp__plugin_dev-docs_dev-docs__write_docs", tool_input)
    # 検証
    assert result.returncode == 0
    assert "decision" not in _output(result)
    assert "| 足す | 追加 |" in _rows(result)


def test_error_when_word_list_missing(knowledge_clone: KnowledgeClone, tmp_path: Path) -> None:
    """フックが読む対応表が無ければ、書き込みを止めずに何も出力しない（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    (clone / _WORD_LIST_COPY).unlink()
    content = "設定を直す。"
    written = tmp_path / "written.md"
    # 実行
    written.write_text(content, encoding="utf-8")
    result = _run_hook(clone, "Write", {"file_path": str(written), "content": content})
    # 検証
    assert written.read_text(encoding="utf-8") == content
    assert result.returncode == 0
    assert result.stdout == ""
    assert str(clone / _WORD_LIST_COPY) in result.stderr
