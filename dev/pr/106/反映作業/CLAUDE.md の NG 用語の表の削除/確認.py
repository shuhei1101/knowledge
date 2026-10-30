"""CLAUDE.md に NG 用語の表が無く、同じフォルダにバックアップがあるかを読むだけで確かめる。"""
from __future__ import annotations

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
BACKUP_NAME = "CLAUDE.md.bak-pr106"
TABLE_MARKER = "NG用語"


def main() -> int:
    """CLAUDE.md ごとに観測した値を 1 行ずつ出す。"""
    failed = False
    for target in TARGETS:
        has_table = TABLE_MARKER in target.read_text(encoding="utf-8")
        has_backup = (target.parent / BACKUP_NAME).is_file()
        ok = not has_table and has_backup
        print(f"{target}（NG 用語の表: {'あり' if has_table else 'なし'}、バックアップ: {'あり' if has_backup else 'なし'}）: {'ok' if ok else 'failed'}")
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
