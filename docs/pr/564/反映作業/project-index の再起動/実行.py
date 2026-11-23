#!/usr/bin/env python3
"""project-index の常駐サーバーを、direct_commit.kinds[] の {id, body: false} に対応したクローンのコードで起動し直す。"""

import sys

sys.dont_write_bytecode = True
sys.path.insert(0, sys.path[0])

import _admin  # noqa: E402

args = sys.argv[1:]
if len(args) > 1 or (args and args[0] != "--dry-run"):
    print("前提確認: failed")
    print(f"引数が不正: {args}", file=sys.stderr)
    sys.exit(1)
dry_run = bool(args)

if not _admin.clone_has_required_commit():
    print("前提確認: failed")
    print(f"クローン {_admin.CLONE} が {_admin.REQUIRED_COMMIT} を含まない", file=sys.stderr)
    sys.exit(1)
try:
    ok, detail = _admin.accepts_body_false()
except Exception as e:  # noqa: BLE001
    print("前提確認: failed")
    print(f"check_project: {e}", file=sys.stderr)
    sys.exit(1)
print("前提確認: ok")

# 計画
if ok:
    print("再起動: skipped")
    sys.exit(0)
print(f"動いているサーバーが body: false を受け付けない: {detail}")
if dry_run:
    print("再起動: changed")
    sys.exit(0)

# 適用
try:
    result = _admin.restart(lambda: _admin.accepts_body_false()[0])
except Exception as e:  # noqa: BLE001
    print("再起動: failed")
    print(f"tools/call restart: {e}", file=sys.stderr)
    sys.exit(1)
print(f"再起動: {result}")
