"""10 個の Claude Code の設定の RULE_INJECT_INDEXES_USER から、knowledge の索引だけを除く。

Usage:
python3 "dev/pr/176/反映作業/knowledge の索引の登録/切り戻し.py"
"""

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

# 除く knowledge の索引（メインのクローンの master）
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

# env の RULE_INJECT_INDEXES_USER の行（値はカンマ区切りの索引）
_ENTRY = re.compile(r'^(?P<head>\s*"RULE_INJECT_INDEXES_USER": ")(?P<value>[^"]*)(?P<tail>",?\s*)$', re.MULTILINE)


def main() -> int:
    """設定ごとに索引の並びから knowledge の索引を除き、他の値と他の索引は変えない。"""
    failed = False
    for name in SETTINGS:
        path = Path(name)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            print(f"設定（{name}）: failed")
            failed = True
            continue
        matched = _ENTRY.search(text)
        if matched is None:
            print(f"索引の行（{name}）: failed")
            failed = True
            continue
        indexes = [item.strip() for item in matched.group("value").split(",") if item.strip()]
        # 既に入っていなければ何もしない
        if KNOWLEDGE_INDEX not in indexes:
            print(f"索引の削除（{name}）: skipped")
            continue
        value = ",".join(item for item in indexes if item != KNOWLEDGE_INDEX)
        new = text[: matched.start("value")] + value + text[matched.end("value") :]
        # 検証してから一時ファイルで置き換える
        try:
            json.loads(new)
        except ValueError:
            print(f"検証（{name}）: failed")
            failed = True
            continue
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            handle.write(new)
        shutil.copymode(path, handle.name)
        Path(handle.name).replace(path)
        print(f"索引の削除（{name}）: changed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
