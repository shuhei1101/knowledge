#!/usr/bin/env python3
"""project-index の管理の MCP とクローンへ読み取りだけでつながるかを確かめる。"""

import sys

sys.dont_write_bytecode = True
sys.path.insert(0, sys.path[0])

import _admin  # noqa: E402

failed = False
try:
    st = _admin.status()
    print(f"管理の MCP の status: ok（pid {st.get('pid')}）")
except Exception as e:  # noqa: BLE001
    print("管理の MCP の status: failed")
    print(f"POST {_admin.URL} tools/call status: {e}", file=sys.stderr)
    failed = True
if _admin.clone_has_required_commit():
    print(f"クローンの commit（{_admin.REQUIRED_COMMIT} を含む）: ok")
else:
    print(f"クローンの commit（{_admin.REQUIRED_COMMIT} を含む）: failed")
    print(f"git -C {_admin.CLONE} merge-base --is-ancestor {_admin.REQUIRED_COMMIT} HEAD が 0 以外", file=sys.stderr)
    failed = True
sys.exit(1 if failed else 0)
