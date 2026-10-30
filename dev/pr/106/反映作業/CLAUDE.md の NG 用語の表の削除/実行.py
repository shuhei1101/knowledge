"""プラグインを入れた設定フォルダの CLAUDE.md から `## カタカナ英語縛りしないでください` のセクションを削除する。"""
from __future__ import annotations

import difflib
import json
import shutil
import sys
import tempfile
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
SECTION_HEADING = "## カタカナ英語縛りしないでください\n"
PLUGIN_ID = "knowledge@knowledge"


def plan(lines: list[str]) -> list[str] | None:
    """セクションを除いた行の並びを返す（セクションが 2 つ以上あれば None）。"""
    count = lines.count(SECTION_HEADING)
    if count > 1:
        return None
    if count == 0:
        return lines
    start = lines.index(SECTION_HEADING)
    # セクションの範囲は次の `## ` で始まる見出しの手前まで
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    head = lines[:start]
    # 末尾のセクションを消すときは、直前の空行も落とす
    if end == len(lines):
        while head and head[-1].strip() == "":
            head.pop()
    return head + lines[end:]


def plugin_installed(target: Path) -> bool:
    """CLAUDE.md と同じ設定フォルダに knowledge@knowledge が入っているかを返す。"""
    installed = target.parent / "plugins" / "installed_plugins.json"
    if not installed.is_file():
        return False
    return PLUGIN_ID in json.loads(installed.read_text(encoding="utf-8")).get("plugins", {})


def main() -> int:
    """前提確認 → 計画 → 適用の順にセクションを削除する。"""
    # 前提確認
    if not all(target.is_file() for target in TARGETS):
        print("前提確認: failed")
        return 1
    contents = {target: target.read_text(encoding="utf-8").splitlines(keepends=True) for target in TARGETS}
    plans = {target: plan(lines) for target, lines in contents.items()}
    if any(new is None for new in plans.values()):
        print("前提確認: failed")
        return 1
    print("前提確認: ok")
    # 計画（--dry-run もここを通る）
    changes = {target: new for target, new in plans.items() if new != contents[target]}
    for target in TARGETS:
        if target in changes:
            sys.stdout.writelines(difflib.unified_diff(contents[target], changes[target], str(target), str(target)))
        else:
            print(f"{target} のセクションの削除: skipped")
    if sys.argv[1:] == ["--dry-run"]:
        for target in changes:
            print(f"{target} のセクションの削除: changed")
        return 0
    # 適用（検証 → 退避 → 置き換え）
    for target, new in changes.items():
        if SECTION_HEADING in new or not plugin_installed(target):
            print(f"{target} の検証: failed")
            return 1
        print(f"{target} の検証: ok")
        backup = target.parent / BACKUP_NAME
        shutil.copy2(target, backup)
        # バックアップから戻せることを確かめる
        if backup.read_bytes() != target.read_bytes():
            print(f"{target} のバックアップ: failed")
            return 1
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as tmp:
            tmp.writelines(new)
        shutil.copymode(target, tmp.name)
        Path(tmp.name).replace(target)
        print(f"{target} のセクションの削除: changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
