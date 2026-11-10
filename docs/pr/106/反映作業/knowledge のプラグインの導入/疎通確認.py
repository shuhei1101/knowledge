"""プラグインを入れる設定フォルダ・claude コマンド・マーケットプレイスのリポジトリへ読み取りだけでつながるかを確かめる。"""
from __future__ import annotations

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
MARKETPLACE_URL = "https://github.com/shuhei1101/knowledge.git"
COMMAND_TIMEOUT_SEC = 60


def main() -> int:
    """設定フォルダごと・claude コマンド・マーケットプレイスのリポジトリの結果を 1 行ずつ出す。"""
    failed = False
    for config_dir in CONFIG_DIRS:
        ok = (config_dir / "CLAUDE.md").is_file()
        print(f"{config_dir} の設定フォルダ: {'ok' if ok else 'failed'}")
        failed |= not ok
    claude = shutil.which("claude")
    ok = claude is not None and subprocess.run(
        [claude, "--version"], capture_output=True, timeout=COMMAND_TIMEOUT_SEC
    ).returncode == 0
    print(f"claude コマンド: {'ok' if ok else 'failed'}")
    failed |= not ok
    ok = subprocess.run(
        ["git", "ls-remote", "--", MARKETPLACE_URL, "HEAD"], capture_output=True, timeout=COMMAND_TIMEOUT_SEC
    ).returncode == 0
    print(f"マーケットプレイスのリポジトリ: {'ok' if ok else 'failed'}")
    failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
