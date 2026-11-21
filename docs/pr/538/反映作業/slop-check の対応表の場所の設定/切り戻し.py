"""実行で退避した settings.json を書き戻す。"""

from __future__ import annotations

import shutil
import sys

from _common import BACKUP_SUFFIX, SETTINGS


def main() -> int:
    for path in SETTINGS:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if not backup.is_file():
            print(f"{path} の書き戻し: skipped")
            continue
        shutil.copy2(backup, path)
        print(f"{path} の書き戻し: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
