"""10 個の Claude Code の設定の RULE_INJECT_INDEXES_USER に、knowledge の索引をカンマ区切りで追加する。

Usage:
# 変わる設定と差分だけを出す
python3 "dev/pr/176/反映作業/knowledge の索引の登録/実行.py" --dry-run
# 適用する（設定ごとに settings.json.bak-pr176 へ退避してから置き換える）
python3 "dev/pr/176/反映作業/knowledge の索引の登録/実行.py"
"""

import argparse
import difflib
import json
import re
import shutil
import sys
import tempfile
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

# 退避するファイルの接尾辞
BACKUP_SUFFIX = ".bak-pr176"

# env の RULE_INJECT_INDEXES_USER の行（値はカンマ区切りの索引）
_ENTRY = re.compile(r'^(?P<head>\s*"RULE_INJECT_INDEXES_USER": ")(?P<value>[^"]*)(?P<tail>",?\s*)$', re.MULTILINE)


def _plan(text: str) -> str | None:
    """knowledge の索引を加えた後の中身を返す。既に入っていれば None。"""
    matched = _ENTRY.search(text)
    if matched is None:
        message = "RULE_INJECT_INDEXES_USER の行がありません"
        raise ValueError(message)
    indexes = [item.strip() for item in matched.group("value").split(",") if item.strip()]
    if KNOWLEDGE_INDEX in indexes:
        return None
    value = ",".join([*indexes, KNOWLEDGE_INDEX])
    return text[: matched.start("value")] + value + text[matched.end("value") :]


def main(argv: list[str] | None = None) -> int:
    """全ての設定を計画し、--dry-run でなければ退避してから置き換える。"""
    parser = argparse.ArgumentParser(description="RULE_INJECT_INDEXES_USER に knowledge の索引を追加する")
    parser.add_argument("--dry-run", action="store_true", help="差分だけを出して書き換えない")
    args = parser.parse_args(argv)

    # 前提確認: 全ての設定が読め、JSON として正しく、索引の行を持つ
    plans: list[tuple[Path, str, str | None]] = []
    for name in SETTINGS:
        path = Path(name)
        try:
            text = path.read_text(encoding="utf-8")
            json.loads(text)
            plans.append((path, text, _plan(text)))
        except (OSError, ValueError) as error:
            print(f"前提確認（{path}）: failed {error}")
            return 1
    print("前提確認: ok")

    failed = False
    for path, text, new in plans:
        # 計画: 既に入っていれば何もしない
        if new is None:
            print(f"索引の追加（{path}）: skipped")
            continue
        sys.stdout.writelines(
            difflib.unified_diff(
                text.splitlines(keepends=True), new.splitlines(keepends=True), str(path), str(path)
            )
        )
        if args.dry_run:
            print(f"索引の追加（{path}）: changed")
            continue
        # 適用: 検証 → 退避 → 一時ファイルから置き換え
        try:
            value = json.loads(new)["env"]["RULE_INJECT_INDEXES_USER"]
        except (ValueError, KeyError) as error:
            print(f"検証（{path}）: failed {error}")
            failed = True
            continue
        if KNOWLEDGE_INDEX not in value.split(","):
            print(f"検証（{path}）: failed")
            failed = True
            continue
        shutil.copy2(path, f"{path}{BACKUP_SUFFIX}")
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            handle.write(new)
        shutil.copymode(path, handle.name)
        Path(handle.name).replace(path)
        print(f"索引の追加（{path}）: changed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
