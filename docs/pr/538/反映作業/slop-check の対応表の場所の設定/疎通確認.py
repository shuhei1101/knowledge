"""対象の settings.json と、指す対応表のコピーに、読み取りだけでつながるかを確かめる。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import SETTINGS, VALUE


def main() -> int:
    failed = False
    for path in SETTINGS:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            print(f"{path}: failed")
            print(f"{path}: {error}", file=sys.stderr)
            failed = True
            continue
        print(f"{path}: ok")
    if Path(VALUE).is_file():
        print("対応表のコピー: ok")
    else:
        print("対応表のコピー: failed")
        print(f"{VALUE} がありません", file=sys.stderr)
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
