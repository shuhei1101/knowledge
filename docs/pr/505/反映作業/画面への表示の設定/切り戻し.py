#!/usr/bin/env -S python3 -B
"""各 settings.json の env から、実行で記載した SLOP_CHECK_SHOW_ADDED を削除する。"""

import json
import os
import sys
import tempfile
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
KEY = "SLOP_CHECK_SHOW_ADDED"
VALUE = "1"


def main() -> int:
    for path in TARGETS:
        if not path.is_file():
            print(f"{path}: skipped")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        env = data.get("env")
        # 実行で記載した値が無ければ何もしない
        if not isinstance(env, dict) or env.get(KEY) != VALUE:
            print(f"{path}: skipped")
            continue
        del env[KEY]
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".settings.", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        os.chmod(tmp, path.stat().st_mode)
        os.replace(tmp, path)
        print(f"{path}: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
