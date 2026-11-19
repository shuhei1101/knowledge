#!/usr/bin/env -S python3 -B
"""slop-check を有効にした Claude Code の settings.json の env に SLOP_CHECK_SHOW_ADDED を記載する。"""

import datetime
import difflib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HOME = Path.home()
TARGETS = [
    HOME / ".claude/settings.json",
    HOME / ".claude-dev/settings.json",
    HOME / ".claude-dev1/settings.json",
    HOME / ".claude-sub/settings.json",
    HOME / ".claude-sub2/settings.json",
    HOME / ".claude-sub3/settings.json",
    HOME / ".claude-sub4/settings.json",
    HOME / ".claude-sub5/settings.json",
    HOME / ".claude-sub6/settings.json",
    HOME / ".claude-sub7/settings.json",
]
PLUGIN = "slop-check@knowledge"
KEY = "SLOP_CHECK_SHOW_ADDED"
VALUE = "1"


def render(data: dict[str, object]) -> str:
    """settings.json と同じ 2 字下げ・末尾改行の JSON にする。"""
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    # 前提確認: 引数は無し（本番）か --dry-run だけ
    args = sys.argv[1:]
    if len(args) > 1 or (args and args[0] != "--dry-run"):
        print("前提確認: failed")
        print(f"受け付けない引数: {args}", file=sys.stderr)
        return 1
    dry_run = bool(args)
    missing = [str(p) for p in TARGETS if not p.is_file()]
    if len(missing) == len(TARGETS):
        print("前提確認: failed")
        print("対象の settings.json が 1 件も無い", file=sys.stderr)
        return 1
    print("前提確認: ok")

    # 計画: 対象ごとに書き換え後の内容を作る（--dry-run もここを通る）
    plans: list[tuple[Path, str]] = []
    for path in TARGETS:
        label = f"{path}"
        # ファイルが無い端末の設定は対象にしない
        if not path.is_file():
            print(f"{label}: skipped")
            continue
        current = path.read_text(encoding="utf-8")
        data = json.loads(current)
        plugins = data.get("enabledPlugins", {})
        # slop-check を有効にしていない設定は書き換えない
        if not isinstance(plugins, dict) or plugins.get(PLUGIN) is not True:
            print(f"{label}: skipped")
            continue
        env = data.setdefault("env", {})
        if not isinstance(env, dict):
            print(f"{label}: failed")
            print(f"env がオブジェクトでない: {type(env).__name__}", file=sys.stderr)
            return 1
        # 既に表示する値なら何もしない
        if env.get(KEY) == VALUE:
            print(f"{label}: skipped")
            continue
        env[KEY] = VALUE
        new = render(data)
        sys.stdout.writelines(
            difflib.unified_diff(
                current.splitlines(keepends=True),
                new.splitlines(keepends=True),
                fromfile=str(path),
                tofile=str(path),
            )
        )
        plans.append((path, new))
        if dry_run:
            print(f"{label}: changed")
    if dry_run:
        return 0

    # 適用: 一時ファイルへ記載 → 検証 → 退避 → 置き換え
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for path, new in plans:
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".settings.", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new)
        written = json.loads(Path(tmp).read_text(encoding="utf-8"))
        # 記載した内容に表示する値が入っていなければ元のファイルに触れずに止める
        if written.get("env", {}).get(KEY) != VALUE:
            os.unlink(tmp)
            print(f"{path} の検証: failed")
            return 1
        shutil.copy2(path, path.with_name(f"{path.name}.bak-{stamp}"))
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
        print(f"{path}: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
