"""端末の設定の knowledge の行の direct_commit.scope を空に戻し、knowledge の配信元を再読み込みする。"""

from __future__ import annotations

import sys

from _common import API, SOURCE_ID, find_row, request


def main() -> int:
    status, body = request("GET", API)
    row = find_row(body) if status == 200 else None
    if row is None:
        print("前提確認: failed")
        return 1
    if not (row.get("directCommit") or {}).get("scope"):
        print("direct_commit.scope の削除: skipped")
        return 0
    payload = {"expectedVersion": body["version"], "source": {"direct_commit": {"scope": []}}}
    status, result = request("PATCH", f"{API}/{SOURCE_ID}", payload)
    if status != 200:
        print("direct_commit.scope の削除: failed")
        print(f"PATCH {API}/{SOURCE_ID}: HTTP {status} {result}", file=sys.stderr)
        return 1
    print("direct_commit.scope の削除: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
