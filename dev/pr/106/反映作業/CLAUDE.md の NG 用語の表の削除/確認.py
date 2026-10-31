"""CLAUDE.md の実体に NG 用語の表が無く、実体の隣にバックアップがあり、シンボリックリンクが実体を指したままかを読むだけで確かめる。"""
from __future__ import annotations

from pathlib import Path

REAL_TARGET = Path.home() / ".claude" / "CLAUDE.md"
LINKED_TARGETS = [
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
    """実体とリンクごとに観測した値を 1 行ずつ出す。"""
    has_table = TABLE_MARKER in REAL_TARGET.read_text(encoding="utf-8")
    backup = REAL_TARGET.parent / BACKUP_NAME
    has_backup = backup.is_file() and TABLE_MARKER in backup.read_text(encoding="utf-8")
    failed = has_table or not has_backup
    print(
        f"{REAL_TARGET}（NG 用語の表: {'あり' if has_table else 'なし'}、表を持つバックアップ: {'あり' if has_backup else 'なし'}）: "
        f"{'failed' if failed else 'ok'}"
    )
    for link in LINKED_TARGETS:
        ok = link.is_symlink() and link.resolve() == REAL_TARGET.resolve()
        print(f"{link} のリンク先（{link.resolve()}）: {'ok' if ok else 'failed'}")
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
