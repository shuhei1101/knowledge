"""設定フォルダごとに knowledge@knowledge が有効で、入ったフックが語の選び方の要点を出すかを読むだけで確かめる。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

CONFIG_DIRS = [
    Path.home() / ".claude",
    Path.home() / ".claude-dev",
    Path.home() / ".claude-dev1",
    Path.home() / ".claude-sub",
    Path.home() / ".claude-sub2",
    Path.home() / ".claude-sub3",
    Path.home() / ".claude-sub4",
    Path.home() / ".claude-sub5",
    Path.home() / ".claude-sub6",
    Path.home() / ".claude-sub7",
]
PLUGIN_ID = "knowledge@knowledge"
HOOK_SCRIPT = Path("hooks") / "session-start" / "inject-word-choice.sh"
HOOK_INPUT = '{"hook_event_name":"SessionStart","source":"startup"}'
EXPECTED_HEADINGS = ["原則（悪い例 → 良い例）:", "ドキュメントの語の対応（避ける語 → 使う語）:"]
COMMAND_TIMEOUT_SEC = 60


def check(claude: str, config_dir: Path) -> tuple[bool, str]:
    """設定フォルダのプラグインの状態と、フックの出力を観測した値を返す。"""
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config_dir)}
    listed = subprocess.run(
        [claude, "plugin", "list", "--json"], env=env, capture_output=True, text=True, timeout=COMMAND_TIMEOUT_SEC
    )
    plugin = next((p for p in json.loads(listed.stdout or "[]") if p.get("id") == PLUGIN_ID), None)
    if plugin is None:
        return False, "未導入"
    if not plugin.get("enabled"):
        return False, "無効"
    hook = Path(plugin["installPath"]) / HOOK_SCRIPT
    output = subprocess.run(
        ["bash", str(hook)],
        input=HOOK_INPUT,
        env={**os.environ, "CLAUDE_PLUGIN_ROOT": plugin["installPath"]},
        capture_output=True,
        text=True,
        timeout=COMMAND_TIMEOUT_SEC,
    )
    context = json.loads(output.stdout or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
    if not all(heading in context for heading in EXPECTED_HEADINGS):
        return False, f"有効、フックの出力 {len(context)} 文字で原則表か対応表が無い"
    return True, f"有効、フックの出力 {len(context)} 文字"


def main() -> int:
    """設定フォルダごとの観測した値を 1 行ずつ出す。"""
    claude = shutil.which("claude")
    if claude is None:
        print("claude コマンド: failed")
        return 1
    failed = False
    for config_dir in CONFIG_DIRS:
        ok, observed = check(claude, config_dir)
        print(f"{config_dir} の {PLUGIN_ID}（{observed}）: {'ok' if ok else 'failed'}")
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
