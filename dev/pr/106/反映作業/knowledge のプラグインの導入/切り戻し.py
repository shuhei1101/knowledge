"""settings.json だけ別の設定フォルダでプラグイン knowledge@knowledge を無効にしてから、プラグインを外してマーケットプレイス knowledge の登録を削除する。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
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
MARKETPLACE_NAME = "knowledge"
PLUGIN_ID = "knowledge@knowledge"
COMMAND_TIMEOUT_SEC = 300


def read_json(path: Path) -> dict:
    """JSON ファイルを読む（ファイルが無ければ空の辞書）。"""
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def plan() -> list[tuple[Path, str, list[str]]]:
    """実体の plugins/ と settings.json ごとに 1 回だけ流すコマンドを、設定フォルダ・手順の名前とあわせて返す。"""
    disables = []
    removals = []
    done_plugins: set[Path] = set()
    done_settings: set[Path] = set()
    for config_dir in CONFIG_DIRS:
        plugins_dir = (config_dir / "plugins").resolve()
        settings = (config_dir / "settings.json").resolve()
        if plugins_dir not in done_plugins:
            done_plugins.add(plugins_dir)
            done_settings.add(settings)
            if PLUGIN_ID in read_json(plugins_dir / "installed_plugins.json").get("plugins", {}):
                removals.append((config_dir, "プラグインの削除", ["uninstall", PLUGIN_ID]))
            if MARKETPLACE_NAME in read_json(plugins_dir / "known_marketplaces.json"):
                removals.append((config_dir, "マーケットプレイスの登録の削除", ["marketplace", "remove", MARKETPLACE_NAME]))
            continue
        if settings in done_settings:
            continue
        done_settings.add(settings)
        if read_json(settings).get("enabledPlugins", {}).get(PLUGIN_ID) is True:
            disables.append((config_dir, "プラグインの無効化", ["disable", PLUGIN_ID]))
    # 無効化はプラグインが入っている間にしか流せないため、削除より先に流す
    return disables + removals


def main() -> int:
    """外す手順を流し、結果を 1 行ずつ出す。"""
    claude = shutil.which("claude")
    if claude is None:
        print("claude コマンド: failed")
        return 1
    steps = plan()
    if not steps:
        print("プラグインの削除: skipped")
        return 0
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
