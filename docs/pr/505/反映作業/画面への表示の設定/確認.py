#!/usr/bin/env -S python3 -B
"""slop-check を有効にした各 settings.json の env.SLOP_CHECK_SHOW_ADDED が "1" かを観測する。"""

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
PLUGIN = "slop-check@knowledge"
KEY = "SLOP_CHECK_SHOW_ADDED"
VALUE = "1"


def main() -> int:
    failed = False
    for path in TARGETS:
        if not path.is_file():
            print(f"{path}: skipped")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        plugins = data.get("enabledPlugins", {})
        # slop-check を有効にしていない設定は観測しない
        if not isinstance(plugins, dict) or plugins.get(PLUGIN) is not True:
            print(f"{path}: skipped")
            continue
        value = data.get("env", {}).get(KEY)
        if value == VALUE:
            print(f"{path} の {KEY}: ok")
        else:
            print(f"{path} の {KEY}: failed")
            print(f"観測した値: {value!r}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
