"""ネットミームの配信元の行が配信中で、端末の設定のファイルに direct_commit.scope があるかを読むだけで確かめる。"""

from __future__ import annotations

import sys

from _common import API, SETTINGS, SOURCE_ID, request


def main() -> int:
    status, body = request("GET", API)
    rows = {row.get("id"): row for row in body.get("sources", [])} if status == 200 else {}
    row = rows.get(SOURCE_ID)
    if row is None or row.get("status") != "serving":
        print(f"配信元の状態: failed（{None if row is None else row.get('status')}）")
        return 1
    print("配信元の状態: ok（serving）")
    text = SETTINGS.read_text(encoding="utf-8")
    if "/home/shuhei2441/**" not in text.split(f"id: {SOURCE_ID}", 1)[-1]:
        print("direct_commit.scope: failed")
        return 1
    print("direct_commit.scope: ok（/home/shuhei2441/**）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
