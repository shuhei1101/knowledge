#!/usr/bin/env -S python3 -B
"""対象の settings.json を JSON として読み込めるかを、状態を変えずに確認する。"""

import json
import sys
from pathlib import Path

HOME = Path.home()
TARGETS = [
    HOME / ".claude/settings.json",
    HOME / ".claude-dev/settings.json",
    HOME / ".claude-dev1/settings.json",
    HOME / ".claude-sub/settings.json",
    HOME / ".claude-sub2/settings.json",
    HOME / ".claude-sub3/settings.json",
    HOME / ".claude-sub4/settings.json",
    HOME / ".claude-sub5/settings.json",
    HOME / ".claude-sub6/settings.json",
    HOME / ".claude-sub7/settings.json",
]


def main() -> int:
    failed = False
    for path in TARGETS:
        # ファイルが無い端末の設定は対象外
        if not path.is_file():
            print(f"{path}: skipped")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"{path}: failed")
            print(f"読み込めない: {e}", file=sys.stderr)
            failed = True
            continue
        print(f"{path}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
