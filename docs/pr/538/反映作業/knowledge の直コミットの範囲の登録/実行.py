"""端末の設定の knowledge の行に direct_commit.scope を追加し、knowledge の配信元を再読み込みする。

Usage:
# 計画だけを出す
python3 -B 実行.py --dry-run
# 適用する
python3 -B 実行.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _common import API, CONFIG, SCOPE, SOURCE_ID, find_row, request


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
    row = find_row(body) if status == 200 else None
    if status != 200 or "version" not in body or row is None:
        print("前提確認: failed")
        print(f"GET {API}: HTTP {status} {body}", file=sys.stderr)
        return 1
    config = Path(CONFIG)
    if not config.is_file() or "\ndirect_commit:" not in config.read_text(encoding="utf-8"):
        print("前提確認: failed")
        print(f"{CONFIG} に direct_commit がありません（develop へマージした後に実行する）", file=sys.stderr)
        return 1
    print("前提確認: ok")

    # 計画（--dry-run もここを通る）
    current = (row.get("directCommit") or {}).get("scope") or []
    if current == SCOPE:
        print("direct_commit.scope の追加: skipped")
        return 0
    print(f"--- sources[{SOURCE_ID}].direct_commit.scope")
    print(f"+++ sources[{SOURCE_ID}].direct_commit.scope")
    print(f"-{json.dumps(current, ensure_ascii=False)}")
    print(f"+{json.dumps(SCOPE, ensure_ascii=False)}")
    if args.dry_run:
        print("direct_commit.scope の追加: changed")
        return 0

    # 適用（変更と再読み込みは API が行い、書き換える前のファイルは API が退避しないため切り戻しは同じ API で戻す）
    payload = {"expectedVersion": body["version"], "source": {"direct_commit": {"scope": SCOPE}}}
    status, result = request("PATCH", f"{API}/{SOURCE_ID}", payload)
    if status != 200:
        print("direct_commit.scope の追加: failed")
        print(f"PATCH {API}/{SOURCE_ID}: HTTP {status} {result}", file=sys.stderr)
        return 1
    print("direct_commit.scope の追加: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
