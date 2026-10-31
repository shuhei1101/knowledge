"""マーケットプレイス shuhei1101/knowledge を登録してプラグイン knowledge@knowledge を入れ、各設定フォルダの settings.json で有効にする。"""
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


def read_json(path: Path) -> dict:
    """JSON ファイルを読む（ファイルが無ければ空の辞書）。"""
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def plan() -> list[tuple[Path, str, list[str]]]:
    """実体の plugins/ と settings.json ごとに 1 回だけ流すコマンドを、設定フォルダ・手順の名前とあわせて返す。"""
    steps = []
    done_plugins: set[Path] = set()
    done_settings: set[Path] = set()
    for config_dir in CONFIG_DIRS:
        plugins_dir = (config_dir / "plugins").resolve()
        settings = (config_dir / "settings.json").resolve()
        # 実体の plugins/ へ初めて当たった設定フォルダで、登録と導入をする（導入はその settings.json でも有効にする）
        if plugins_dir not in done_plugins:
            done_plugins.add(plugins_dir)
            done_settings.add(settings)
            if MARKETPLACE_NAME in read_json(plugins_dir / "known_marketplaces.json"):
                steps.append((config_dir, "マーケットプレイスの更新", ["marketplace", "update", MARKETPLACE_NAME]))
            else:
                steps.append((config_dir, "マーケットプレイスの登録", ["marketplace", "add", MARKETPLACE_SOURCE]))
            if PLUGIN_ID in read_json(plugins_dir / "installed_plugins.json").get("plugins", {}):
                steps.append((config_dir, "プラグインの更新", ["update", PLUGIN_ID]))
            else:
                steps.append((config_dir, "プラグインの導入", ["install", PLUGIN_ID]))
            continue
        # plugins/ を共有し settings.json だけ別の設定フォルダは、有効にするだけ
        if settings in done_settings:
            continue
        done_settings.add(settings)
        if read_json(settings).get("enabledPlugins", {}).get(PLUGIN_ID) is not True:
            steps.append((config_dir, "プラグインの有効化", ["enable", PLUGIN_ID]))
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
    steps = plan()
    for config_dir, _, args in steps:
        print(f"CLAUDE_CONFIG_DIR={config_dir} claude plugin {' '.join(args)}")
    if sys.argv[1:] == ["--dry-run"]:
        for config_dir, name, _ in steps:
            print(f"{config_dir} の{name}: changed")
        return 0
    # 適用（失敗した手順で止める。冪等でない操作は再試行しない）
    for config_dir, name, args in steps:
        env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config_dir)}
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
