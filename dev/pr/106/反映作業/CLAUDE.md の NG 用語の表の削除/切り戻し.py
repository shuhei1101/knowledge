"""実行で退避した CLAUDE.md の実体を元へ戻す。"""
from __future__ import annotations

import shutil
from pathlib import Path

REAL_TARGET = Path.home() / ".claude" / "CLAUDE.md"
BACKUP_NAME = "CLAUDE.md.bak-pr106"


def main() -> int:
    """退避したファイルで CLAUDE.md の実体を置き換える。"""
    backup = REAL_TARGET.parent / BACKUP_NAME
    # 退避したファイルが無い: 戻す元が無い
    if not backup.is_file():
        print("退避したファイル: failed")
        return 1
    shutil.copy2(backup, REAL_TARGET)
    print(f"{REAL_TARGET} の書き戻し: changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
