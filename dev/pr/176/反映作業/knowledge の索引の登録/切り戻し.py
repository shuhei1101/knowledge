"""実行で退避した settings.json.bak-pr176 から、10 個の Claude Code の設定を元に戻す。

Usage:
python3 "dev/pr/176/反映作業/knowledge の索引の登録/切り戻し.py"
"""

import shutil
import sys
from pathlib import Path

# 書き換えた 10 個の Claude Code の設定
SETTINGS = (
    "/home/shuhei2441/.claude/settings.json",
    "/home/shuhei2441/.claude-dev/settings.json",
    "/home/shuhei2441/.claude-dev1/settings.json",
    "/home/shuhei2441/.claude-sub/settings.json",
    "/home/shuhei2441/.claude-sub2/settings.json",
    "/home/shuhei2441/.claude-sub3/settings.json",
    "/home/shuhei2441/.claude-sub4/settings.json",
    "/home/shuhei2441/.claude-sub5/settings.json",
    "/home/shuhei2441/.claude-sub6/settings.json",
    "/home/shuhei2441/.claude-sub7/settings.json",
)

# 実行が退避したファイルの接尾辞
BACKUP_SUFFIX = ".bak-pr176"


def main() -> int:
    """退避したファイルがある設定を書き戻し、退避が無い設定は failed にする。"""
    failed = False
    for name in SETTINGS:
        backup = Path(f"{name}{BACKUP_SUFFIX}")
        if not backup.is_file():
            print(f"退避したファイル（{backup}）: failed")
            failed = True
            continue
        shutil.copy2(backup, name)
        print(f"設定の書き戻し（{name}）: changed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
