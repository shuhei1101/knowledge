"""NG 用語の表を消す CLAUDE.md を読み取りだけで開けるかを確かめる。"""
from __future__ import annotations

import os
from pathlib import Path

TARGETS = [
    Path.home() / ".claude" / "CLAUDE.md",
    Path.home() / ".claude-dev" / "CLAUDE.md",
    Path.home() / ".claude-dev1" / "CLAUDE.md",
    Path.home() / ".claude-sub" / "CLAUDE.md",
    Path.home() / ".claude-sub2" / "CLAUDE.md",
    Path.home() / ".claude-sub3" / "CLAUDE.md",
    Path.home() / ".claude-sub4" / "CLAUDE.md",
    Path.home() / ".claude-sub5" / "CLAUDE.md",
    Path.home() / ".claude-sub6" / "CLAUDE.md",
    Path.home() / ".claude-sub7" / "CLAUDE.md",
]


def main() -> int:
    """CLAUDE.md ごとの結果を 1 行ずつ出す。"""
    failed = False
    for target in TARGETS:
        ok = target.is_file() and os.access(target, os.R_OK | os.W_OK)
        print(f"{target}: {'ok' if ok else 'failed'}")
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
