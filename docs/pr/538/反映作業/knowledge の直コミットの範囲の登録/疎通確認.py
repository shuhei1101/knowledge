"""端末の設定の API と knowledge の配信元の設定に、読み取りだけでつながるかを確かめる。"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

from _common import API, CONFIG, find_row, request


def main() -> int:
    try:
        status, body = request("GET", API)
    except OSError:
        print("端末の設定の API: failed")
        print(f"GET {API}", file=sys.stderr)
        traceback.print_exc()
        return 1
    if status != 200:
        print("端末の設定の API: failed")
        print(f"GET {API}: HTTP {status}", file=sys.stderr)
        return 1
    print("端末の設定の API: ok")
    if find_row(body) is None:
        print("knowledge の行: failed")
        return 1
    print("knowledge の行: ok")
    if not Path(CONFIG).is_file():
        print("配信元の設定: failed")
        print(f"{CONFIG} がありません", file=sys.stderr)
        return 1
    print("配信元の設定: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
