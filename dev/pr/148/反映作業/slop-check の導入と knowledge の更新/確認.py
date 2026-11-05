"""設定フォルダごとに slop-check@knowledge が有効で、入った knowledge@knowledge の hooks/hooks.json に SessionStart の行が無いかを読むだけで確かめる。"""
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
KNOWLEDGE_ID = "knowledge@knowledge"
SLOP_CHECK_ID = "slop-check@knowledge"
KNOWLEDGE_HOOKS = Path("hooks") / "hooks.json"
COMMAND_TIMEOUT_SEC = 60


def check(claude: str, config_dir: Path) -> tuple[bool, str]:
    """設定フォルダの slop-check の状態と、knowledge のフックの設定を観測した値を返す。"""
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config_dir)}
    listed = subprocess.run(
        [claude, "plugin", "list", "--json"], env=env, capture_output=True, text=True, timeout=COMMAND_TIMEOUT_SEC
    )
    plugins = {p.get("id"): p for p in json.loads(listed.stdout or "[]")}
    slop_check = plugins.get(SLOP_CHECK_ID)
    if slop_check is None:
        return False, "slop-check 未導入"
    if not slop_check.get("enabled"):
        return False, "slop-check 無効"
    knowledge = plugins.get(KNOWLEDGE_ID)
    if knowledge is None:
        return True, "slop-check 有効、knowledge 未導入"
    hooks_path = Path(knowledge["installPath"]) / KNOWLEDGE_HOOKS
    hooks = json.loads(hooks_path.read_text(encoding="utf-8")).get("hooks", {}) if hooks_path.is_file() else {}
    if "SessionStart" in hooks:
        return False, f"slop-check 有効、knowledge {knowledge.get('version')} に SessionStart あり"
    return True, f"slop-check 有効、knowledge {knowledge.get('version')} に SessionStart なし"


def main() -> int:
    """設定フォルダごとの観測した値を 1 行ずつ出す。"""
    claude = shutil.which("claude")
    if claude is None:
        print("claude コマンド: failed")
        return 1
    failed = False
    for config_dir in CONFIG_DIRS:
        ok, observed = check(claude, config_dir)
        print(f"{config_dir}（{observed}）: {'ok' if ok else 'failed'}")
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
