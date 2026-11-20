"""端末の設定の API と端末の設定のファイルに、読み取りだけでつながるかを確かめる。"""

from __future__ import annotations

import sys
import traceback

from _common import API, SETTINGS, request


def main() -> int:
    try:
        status, _ = request("GET", API)
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
    if not SETTINGS.is_file():
        print("端末の設定のファイル: failed")
        print(f"{SETTINGS} がありません", file=sys.stderr)
        return 1
    print("端末の設定のファイル: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
