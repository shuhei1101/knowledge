"""端末の設定の sources[] に、ネットミームの配信元の行（direct_commit.scope を含む）を追加し、配信元を再読み込みする。

Usage:
# 計画だけを出す
python3 -B 実行.py --dry-run
# 適用する
python3 -B 実行.py
"""

from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

from _common import API, CONFIG, ROW, SETTINGS, SOURCE_ID, request


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--dry-run", action="store_true")
    try:
        args = parser.parse_args()
    except SystemExit:
        print("前提確認: failed")
        return 1

    # 前提確認
    status, body = request("GET", API)
    if status != 200 or "version" not in body:
        print("前提確認: failed")
        print(f"GET {API}: HTTP {status} {body}", file=sys.stderr)
        return 1
    if not Path(CONFIG).is_file():
        print("前提確認: failed")
        print(f"{CONFIG} がありません（develop へマージした後に実行する）", file=sys.stderr)
        return 1
    print("前提確認: ok")

    # 計画（--dry-run もここを通る）
    rows = {row.get("id"): row for row in body.get("sources", [])}
    if SOURCE_ID in rows:
        print("配信元の行の追加: skipped")
        return 0
    print(f"--- {SETTINGS}")
    print(f"+++ {SETTINGS}")
    print("+ sources[] に次の行を追加する")
    print(json.dumps(ROW, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("配信元の行の追加: changed")
        return 0

    # 適用（退避 → 追加。追加と再読み込みは API が行う）
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = SETTINGS.with_name(f"{SETTINGS.name}.bak-{stamp}")
    shutil.copy2(SETTINGS, backup)
    print(f"退避: ok（{backup}）")
    status, result = request("POST", API, {"source": ROW, "expected_version": body["version"]})
    if status != 201:
        print("配信元の行の追加: failed")
        print(f"POST {API}: HTTP {status} {result}", file=sys.stderr)
        return 1
    print("配信元の行の追加: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
