#!/usr/bin/env -S python3 -B
"""実行で書き換えた settings.json だけ、env から SLOP_CHECK_SHOW_ADDED を削除する。"""

import datetime
import difflib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HOME = Path.home()
KEY = "SLOP_CHECK_SHOW_ADDED"
VALUE = "1"
# 実行が書き換えた settings.json の一覧（実行.py の RECORD と同じ）
RECORD = (
    Path(os.environ.get("XDG_STATE_HOME", str(HOME / ".local/state")))
    / "slop-check/pr505-show-added.json"
)


def render(data: dict[str, object]) -> str:
    """settings.json と同じ 2 字下げ・末尾改行の JSON にする。"""
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    # 前提確認: 引数は無し（本番）か --dry-run だけ。実行の記録が要る
    args = sys.argv[1:]
    if len(args) > 1 or (args and args[0] != "--dry-run"):
        print("前提確認: failed")
        print(f"受け付けない引数: {args}", file=sys.stderr)
        return 1
    dry_run = bool(args)
    if not RECORD.is_file():
        print("前提確認: failed")
        print(f"実行の記録が無い: {RECORD}", file=sys.stderr)
        return 1
    targets = [Path(row["path"]) for row in json.loads(RECORD.read_text(encoding="utf-8"))]
    print("前提確認: ok")

    # 計画: 記録に載った設定ごとに、キーを除いた内容を作る（--dry-run もここを通る）
    plans: list[tuple[Path, str]] = []
    for path in targets:
        if not path.is_file():
            print(f"{path}: skipped")
            continue
        current = path.read_text(encoding="utf-8")
        data = json.loads(current)
        env = data.get("env")
        # 実行で記載した値が残っていなければ何もしない
        if not isinstance(env, dict) or env.get(KEY) != VALUE:
            print(f"{path}: skipped")
            continue
        del env[KEY]
        new = render(data)
        sys.stdout.writelines(
            difflib.unified_diff(
                current.splitlines(keepends=True),
                new.splitlines(keepends=True),
                fromfile=str(path),
                tofile=str(path),
                n=0,
            )
        )
        plans.append((path, new))
        if dry_run:
            print(f"{path}: changed")
    if dry_run:
        return 0

    # 適用: 一時ファイルへ記載 → 検証 → 退避 → 置き換え
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for path, new in plans:
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".settings.", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new)
        written = json.loads(Path(tmp).read_text(encoding="utf-8"))
        # キーが残っていれば元のファイルに触れずに止める
        if KEY in written.get("env", {}):
            os.unlink(tmp)
            print(f"{path} の検証: failed")
            return 1
        backup = path.with_name(f"{path.name}.bak-{stamp}")
        # 同じ名前のバックアップがあれば上書きせずに止める
        if backup.exists():
            os.unlink(tmp)
            print(f"{backup}: failed")
            return 1
        shutil.copy2(path, backup)
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
        print(f"{path}: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
