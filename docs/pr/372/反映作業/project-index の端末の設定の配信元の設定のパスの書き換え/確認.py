"""project-index の端末の設定の knowledge の行が project-index.yaml を指し、そのファイルがあるかを読むだけで確かめる。"""

import json
import urllib.request

import sys
from pathlib import Path

SETTINGS = Path("/home/shuhei2441/.config/project-index/settings.yaml")
NEW_CONFIG = "/mnt/c/Users/shuhe/repo/knowledge/.claude/worktrees/develop/project-index.yaml"
OLD_CONFIG = "/mnt/c/Users/shuhe/repo/knowledge/.claude/worktrees/develop/dev-docs.yaml"
SOURCES_API = "http://127.0.0.1:8786/settings/sources"


def main() -> int:
    """観測した値を出し、効いていれば 0 で終える。"""
    if not SETTINGS.is_file():
        print("端末の設定: failed")
        print(f"{SETTINGS} がありません", file=sys.stderr)
        return 1
    lines = SETTINGS.read_text(encoding="utf-8").splitlines()
    new_count = sum(
        1
        for line in lines
        if line.strip() == "- " + NEW_CONFIG or line.strip().startswith("- " + NEW_CONFIG + " ")
    )
    old_count = sum(
        1
        for line in lines
        if line.strip() == "- " + OLD_CONFIG or line.strip().startswith("- " + OLD_CONFIG + " ")
    )
    exists = Path(NEW_CONFIG).is_file()
    print(f"project-index.yaml の行: {new_count}")
    print(f"dev-docs.yaml の行: {old_count}")
    print(f"{NEW_CONFIG} の有無: {exists}")
    ok = new_count == 1 and old_count == 0 and exists
    # 稼働中の project-index が書き換えた設定を読み直して配信しているか
    try:
        with urllib.request.urlopen(SOURCES_API, timeout=10) as response:
            rows = json.load(response)["sources"]
    except (OSError, ValueError, KeyError) as error:
        print("project-index の配信の状態: failed")
        print(f"{SOURCES_API}: {error}", file=sys.stderr)
        return 1
    row = next((r for r in rows if r.get("id") == "knowledge"), None)
    served = (
        row is not None and row.get("config") == [NEW_CONFIG] and row.get("status") == "serving"
    )
    print(f"project-index の knowledge の行: {row and (row.get('config'), row.get('status'))}")
    ok = ok and served
    if ok:
        print("knowledge の行: ok")
        return 0
    print("knowledge の行: failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
