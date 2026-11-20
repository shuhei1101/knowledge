"""ネットミームの配信元の行が配信中で、端末の設定のファイルのその行に direct_commit.scope があるかを読むだけで確かめる。"""

from __future__ import annotations

import sys

import yaml

from _common import API, SETTINGS, SOURCE_ID, request


def main() -> int:
    status, body = request("GET", API)
    rows = {row.get("id"): row for row in body.get("sources", [])} if status == 200 else {}
    row = rows.get(SOURCE_ID)
    if row is None or row.get("status") != "serving":
        print(f"配信元の状態: failed（{None if row is None else row.get('status')}）")
        return 1
    print("配信元の状態: ok（serving）")
    # 端末の設定の API の行は direct_commit を返さないため、端末の設定のファイルの同じ id の行を読む
    settings = yaml.safe_load(SETTINGS.read_text(encoding="utf-8")) or {}
    entry = next((s for s in settings.get("sources", []) if s.get("id") == SOURCE_ID), {})
    scope = (entry.get("direct_commit") or {}).get("scope") or []
    if "/home/shuhei2441/**" not in scope:
        print(f"direct_commit.scope: failed（{scope}）")
        return 1
    print("direct_commit.scope: ok（/home/shuhei2441/**）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
