"""対象の settings.json の env の SLOP_CHECK_WORD_LIST が対応表のコピーのパスで、そのファイルがあるかを読むだけで確かめる。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from _common import ENV_KEY, SETTINGS, VALUE


def main() -> int:
    failed = False
    for path in SETTINGS:
        value = json.loads(path.read_text(encoding="utf-8")).get("env", {}).get(ENV_KEY)
        if value == VALUE:
            print(f"{path} の {ENV_KEY}: ok")
        else:
            print(f"{path} の {ENV_KEY}: failed（{value}）")
            failed = True
    if Path(VALUE).is_file():
        print("対応表のコピー: ok")
    else:
        print("対応表のコピー: failed")
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
