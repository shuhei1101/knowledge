"""対象の settings.json の env に SLOP_CHECK_WORD_LIST を追加する。書き換える前に同じフォルダへ退避する。

Usage:
# 計画だけを出す
python3 -B 実行.py --dry-run
# 適用する
python3 -B 実行.py
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from _common import BACKUP_SUFFIX, ENV_KEY, SETTINGS, VALUE


def render(data: dict) -> str:
    """settings.json の中身を、既存の書式（インデント 2・非 ASCII をそのまま）の文字列にする。"""
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--dry-run", action="store_true")
    try:
        args = parser.parse_args()
    except SystemExit:
        print("前提確認: failed")
        return 1

    # 前提確認
    loaded: list[tuple[Path, str, dict]] = []
    for path in SETTINGS:
        try:
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
        except (OSError, ValueError) as error:
            print("前提確認: failed")
            print(f"{path}: {error}", file=sys.stderr)
            return 1
        loaded.append((path, text, data))
    if not Path(VALUE).is_file():
        print("前提確認: failed")
        print(f"{VALUE} がありません", file=sys.stderr)
        return 1
    print("前提確認: ok")

    # 計画（--dry-run もここを通る）
    plans: list[tuple[Path, str]] = []
    for path, text, data in loaded:
        env = data.setdefault("env", {})
        if env.get(ENV_KEY) == VALUE:
            print(f"{path} の env の追加: skipped")
            continue
        env[ENV_KEY] = VALUE
        new = render(data)
        sys.stdout.writelines(
            difflib.unified_diff(text.splitlines(True), new.splitlines(True), str(path), str(path))
        )
        plans.append((path, new))
        print(f"{path} の env の追加: changed")
    if args.dry_run or not plans:
        return 0

    # 適用（一時ファイルに書く → 検証 → 退避 → 置き換え）
    for path, new in plans:
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".settings.", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(new)
        if json.loads(Path(tmp).read_text(encoding="utf-8")).get("env", {}).get(ENV_KEY) != VALUE:
            Path(tmp).unlink()
            print(f"{path} の検証: failed")
            return 1
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
        shutil.copymode(path, tmp)
        Path(tmp).replace(path)
        print(f"{path} の書き換え: changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
