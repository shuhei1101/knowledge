"""実行で退避した CLAUDE.md を元へ戻す。"""
from __future__ import annotations

import shutil
from pathlib import Path

TARGETS = [
    Path.home() / ".claude" / "CLAUDE.md",
    Path.home() / ".claude-dev" / "CLAUDE.md",
    Path.home() / ".claude-dev1" / "CLAUDE.md",
    Path.home() / ".claude-sub" / "CLAUDE.md",
    Path.home() / ".claude-sub2" / "CLAUDE.md",
    Path.home() / ".claude-sub3" / "CLAUDE.md",
    Path.home() / ".claude-sub4" / "CLAUDE.md",
    Path.home() / ".claude-sub5" / "CLAUDE.md",
    Path.home() / ".claude-sub6" / "CLAUDE.md",
    Path.home() / ".claude-sub7" / "CLAUDE.md",
]
BACKUP_NAME = "CLAUDE.md.bak-pr106"


def main() -> int:
    """退避したファイルで CLAUDE.md を置き換え、結果を 1 行ずつ出す。"""
    for target in TARGETS:
        backup = target.parent / BACKUP_NAME
        # 退避したファイルが無い: 実行で変えなかった CLAUDE.md
        if not backup.is_file():
            print(f"{target} の書き戻し: skipped")
            continue
        shutil.copy2(backup, target)
        print(f"{target} の書き戻し: changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
