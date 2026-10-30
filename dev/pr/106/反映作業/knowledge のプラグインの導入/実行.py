"""設定フォルダごとにマーケットプレイス shuhei1101/knowledge を登録し、プラグイン knowledge@knowledge を入れる（登録済みなら更新する）。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG_DIRS = [
    Path.home() / ".claude",
    Path.home() / ".claude-dev",
    Path.home() / ".claude-dev1",
    Path.home() / ".claude-sub",
    Path.home() / ".claude-sub2",
    Path.home() / ".claude-sub3",
    Path.home() / ".claude-sub4",
    Path.home() / ".claude-sub5",
    Path.home() / ".claude-sub6",
    Path.home() / ".claude-sub7",
]
MARKETPLACE_SOURCE = "shuhei1101/knowledge"
MARKETPLACE_NAME = "knowledge"
PLUGIN_ID = "knowledge@knowledge"
COMMAND_TIMEOUT_SEC = 300


def read_json_keys(path: Path, *keys: str) -> set[str]:
    """JSON ファイルのキーの集合を返す（ファイルが無ければ空）。keys を辿った先の辞書のキーを返す。"""
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in keys:
        data = data.get(key, {})
    return set(data)


def plan(config_dir: Path) -> list[tuple[str, list[str]]]:
    """設定フォルダで流す claude plugin のコマンドを、手順の名前とあわせて返す。"""
    plugins_dir = config_dir / "plugins"
    marketplaces = read_json_keys(plugins_dir / "known_marketplaces.json")
    installed = read_json_keys(plugins_dir / "installed_plugins.json", "plugins")
    steps = []
    if MARKETPLACE_NAME in marketplaces:
        steps.append(("マーケットプレイスの更新", ["marketplace", "update", MARKETPLACE_NAME]))
    else:
        steps.append(("マーケットプレイスの登録", ["marketplace", "add", MARKETPLACE_SOURCE]))
    if PLUGIN_ID in installed:
        steps.append(("プラグインの更新", ["update", PLUGIN_ID]))
    else:
        steps.append(("プラグインの導入", ["install", PLUGIN_ID]))
    return steps


def main() -> int:
    """前提確認 → 計画 → 適用の順にプラグインを入れる。"""
    # 前提確認
    claude = shutil.which("claude")
    if claude is None or not all((d / "CLAUDE.md").is_file() for d in CONFIG_DIRS):
        print("前提確認: failed")
        return 1
    print("前提確認: ok")
    # 計画（--dry-run もここを通る）
    plans = {config_dir: plan(config_dir) for config_dir in CONFIG_DIRS}
    for config_dir, steps in plans.items():
        for name, args in steps:
            print(f"{config_dir}: CLAUDE_CONFIG_DIR={config_dir} claude plugin {' '.join(args)}")
    if sys.argv[1:] == ["--dry-run"]:
        for config_dir, steps in plans.items():
            for name, _ in steps:
                print(f"{config_dir} の{name}: changed")
        return 0
    # 適用（失敗した設定フォルダで止める。冪等でない操作は再試行しない）
    for config_dir, steps in plans.items():
        env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config_dir)}
        for name, args in steps:
            result = subprocess.run(
                [claude, "plugin", *args], env=env, capture_output=True, text=True, timeout=COMMAND_TIMEOUT_SEC
            )
            if result.returncode != 0:
                print(result.stderr.strip())
                print(f"{config_dir} の{name}: failed")
                return 1
            print(f"{config_dir} の{name}: changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
