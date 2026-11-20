"""端末の設定の sources[] から、ネットミームの配信元の行を削除し、配信元を再読み込みする。"""

from __future__ import annotations

import sys

from _common import API, SOURCE_ID, request


def main() -> int:
    status, body = request("GET", API)
    if status != 200:
        print("前提確認: failed")
        return 1
    if SOURCE_ID not in {row.get("id") for row in body.get("sources", [])}:
        print("配信元の行の削除: skipped")
        return 0
    status, result = request("DELETE", f"{API}/{SOURCE_ID}?expected_version={body['version']}")
    if status != 200:
        print("配信元の行の削除: failed")
        print(f"DELETE {API}/{SOURCE_ID}: HTTP {status} {result}", file=sys.stderr)
        return 1
    print("配信元の行の削除: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
