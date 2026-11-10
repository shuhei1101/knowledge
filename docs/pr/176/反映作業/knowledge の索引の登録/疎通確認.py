"""10 個の Claude Code の設定と knowledge の索引が、読み取りだけで読めるかを確かめる。

Usage:
python3 "dev/pr/176/反映作業/knowledge の索引の登録/疎通確認.py"
"""

import json
import sys
from pathlib import Path

# 追加する knowledge の索引（メインのクローンの master）
KNOWLEDGE_INDEX = "/mnt/c/Users/shuhe/repo/knowledge/rules.yaml"

# 書き換える 10 個の Claude Code の設定
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
    """設定ごとと索引の結果の行を出し、1 つでも読めなければ 1 を返す。"""
    failed = False
    for name in SETTINGS:
        try:
            env = json.loads(Path(name).read_text(encoding="utf-8"))["env"]
            ok = isinstance(env.get("RULE_INJECT_INDEXES_USER"), str)
        except (OSError, ValueError, KeyError):
            ok = False
        print(f"設定（{name}）: {'ok' if ok else 'failed'}")
        failed = failed or not ok
    index_ok = Path(KNOWLEDGE_INDEX).is_file()
    print(f"knowledge の索引（{KNOWLEDGE_INDEX}）: {'ok' if index_ok else 'failed'}")
    return 1 if failed or not index_ok else 0


if __name__ == "__main__":
    sys.exit(main())
