"""設定フォルダごとにプラグイン knowledge@knowledge を外し、マーケットプレイス knowledge の登録を消す。"""
from __future__ import annotations

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
STEPS = [
    ("プラグインの削除", ["uninstall", "knowledge@knowledge"]),
    ("マーケットプレイスの登録の削除", ["marketplace", "remove", "knowledge"]),
]
COMMAND_TIMEOUT_SEC = 300


def main() -> int:
    """設定フォルダごとに外す手順を流し、結果を 1 行ずつ出す。"""
    claude = shutil.which("claude")
    if claude is None:
        print("claude コマンド: failed")
        return 1
    for config_dir in CONFIG_DIRS:
        env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config_dir)}
        for name, args in STEPS:
            result = subprocess.run(
                [claude, "plugin", *args], env=env, capture_output=True, text=True, timeout=COMMAND_TIMEOUT_SEC
            )
            if result.returncode != 0:
                print(result.stderr.strip())
                print(f"{config_dir} の{name}: failed")
                return 1
            print(f"{config_dir} の{name}: changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
