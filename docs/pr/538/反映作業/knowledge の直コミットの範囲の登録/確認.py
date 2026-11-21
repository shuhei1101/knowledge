"""knowledge の行が配信中で、direct_commit.scope が /home/shuhei2441/** になっているかを読むだけで確かめる。"""

from __future__ import annotations

import sys

from _common import API, SCOPE, find_row, request


def main() -> int:
    status, body = request("GET", API)
    row = find_row(body) if status == 200 else None
    if row is None or row.get("status") != "serving":
        print(f"配信元の状態: failed（{None if row is None else row.get('status')}）")
        return 1
    print("配信元の状態: ok（serving）")
    scope = (row.get("directCommit") or {}).get("scope") or []
    if scope != SCOPE:
        print(f"direct_commit.scope: failed（{scope}）")
        return 1
    print(f"direct_commit.scope: ok（{scope[0]}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
