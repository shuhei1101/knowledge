#!/usr/bin/env python3
"""動いている project-index が {id, body: false} を受け付け、配信元 knowledge を配信しているかを確かめる。"""

import sys

sys.dont_write_bytecode = True
sys.path.insert(0, sys.path[0])

import _admin  # noqa: E402

try:
    st = _admin.wait_loaded()
except Exception as e:  # noqa: BLE001
    print("status: failed")
    print(f"POST {_admin.URL} tools/call status: {e}", file=sys.stderr)
    sys.exit(1)
knowledge = next((s for s in st.get("sources", []) if s.get("id") == "knowledge"), None)
state = knowledge.get("status") if knowledge else None
ok, detail = False, ""
for _ in range(_admin.RETRY_ATTEMPTS):
    try:
        ok, detail = _admin.accepts_body_false()
    except _admin.TransientError as e:
        ok, detail = False, str(e)
    if ok:
        break
    _admin.time.sleep(_admin.LOAD_WAIT_INTERVAL_SEC)
print(f"body: false の受け付け: {'ok' if ok else 'failed'}（{detail}）")
print(f"配信元 knowledge: {'ok' if state == 'serving' else 'failed'}（{state}）")
sys.exit(0 if ok and state == "serving" else 1)
