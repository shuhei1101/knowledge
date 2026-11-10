"""CLAUDE.md の実体に AI Slop対策の見出しが無く、他のセクションがバックアップと一致し、シンボリックリンクが実体を指したままかを読むだけで確かめる。"""
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
BACKUP_NAME = "CLAUDE.md.bak-pr148"
SECTION_MARKER = "## AI Slop対策"


def sections_except_marker(text: str) -> str:
    """AI Slop対策のセクションを除いた本文を、末尾の空行を落として返す。"""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(SECTION_MARKER)), None)
    if start is not None:
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        lines = lines[:start] + lines[end:]
    return "\n".join(lines).rstrip()


def main() -> int:
    """実体とリンクごとに観測した値を 1 行ずつ出す。"""
    text = REAL_TARGET.read_text(encoding="utf-8")
    has_section = SECTION_MARKER in text
    backup = REAL_TARGET.parent / BACKUP_NAME
    backup_text = backup.read_text(encoding="utf-8") if backup.is_file() else ""
    has_backup = SECTION_MARKER in backup_text
    others_match = has_backup and sections_except_marker(backup_text) == sections_except_marker(text)
    failed = has_section or not others_match
    print(
        f"{REAL_TARGET}（AI Slop対策: {'あり' if has_section else 'なし'}、"
        f"セクションを持つバックアップ: {'あり' if has_backup else 'なし'}、"
        f"他のセクション: {'一致' if others_match else '不一致'}）: {'failed' if failed else 'ok'}"
    )
    for link in LINKED_TARGETS:
        ok = link.is_symlink() and link.resolve() == REAL_TARGET.resolve()
        print(f"{link} のリンク先（{link.resolve()}）: {'ok' if ok else 'failed'}")
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
