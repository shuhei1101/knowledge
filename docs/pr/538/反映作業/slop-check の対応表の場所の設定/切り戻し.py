"""対象の settings.json の env から SLOP_CHECK_WORD_LIST だけを削除する。ほかのキーは変えない。"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from _common import ENV_KEY, SETTINGS


def main() -> int:
    for path in SETTINGS:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            print(f"{path} の削除: failed")
            print(f"{path}: {error}", file=sys.stderr)
            return 1
        env = data.get("env", {})
        if ENV_KEY not in env:
            print(f"{path} の削除: skipped")
            continue
        del env[ENV_KEY]
        # 一時ファイルに書く → 検証 → 置き換え
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".settings.", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        if ENV_KEY in json.loads(Path(tmp).read_text(encoding="utf-8")).get("env", {}):
            Path(tmp).unlink()
            print(f"{path} の検証: failed")
            return 1
        shutil.copymode(path, tmp)
        Path(tmp).replace(path)
        print(f"{path} の削除: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
