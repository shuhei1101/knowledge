"""10 個の Claude Code の設定の RULE_INJECT_INDEXES_USER に、knowledge の索引が入っているかを読むだけで確かめる。

Usage:
python3 "dev/pr/176/反映作業/knowledge の索引の登録/確認.py"
"""

import json
import sys
from pathlib import Path

# 追加した knowledge の索引（メインのクローンの master）
KNOWLEDGE_INDEX = "/mnt/c/Users/shuhe/repo/knowledge/rules.yaml"

# 書き換えた 10 個の Claude Code の設定
SETTINGS = (
    "/home/shuhei2441/.claude/settings.json",
    "/home/shuhei2441/.claude-dev/settings.json",
    "/home/shuhei2441/.claude-dev1/settings.json",
    "/home/shuhei2441/.claude-sub/settings.json",
    "/home/shuhei2441/.claude-sub2/settings.json",
    "/home/shuhei2441/.claude-sub3/settings.json",
    "/home/shuhei2441/.claude-sub4/settings.json",
    "/home/shuhei2441/.claude-sub5/settings.json",
    "/home/shuhei2441/.claude-sub6/settings.json",
    "/home/shuhei2441/.claude-sub7/settings.json",
)


def main() -> int:
    """設定ごとに観測した索引の並びを出し、1 つでも入っていなければ 1 を返す。"""
    failed = False
    for name in SETTINGS:
        try:
            value = json.loads(Path(name).read_text(encoding="utf-8"))["env"]["RULE_INJECT_INDEXES_USER"]
        except (OSError, ValueError, KeyError):
            value = ""
        ok = KNOWLEDGE_INDEX in [item.strip() for item in value.split(",")]
        print(f"索引（{name}）: {'ok' if ok else 'failed'} {value}")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
