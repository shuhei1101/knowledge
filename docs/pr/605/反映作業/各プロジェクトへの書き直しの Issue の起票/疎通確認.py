"""監視対象の設定と、各プロジェクトのクローンを参照できるかを確認する。"""

import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True
SETTINGS = Path.home() / ".config/ai-monitor/settings.yaml"


def main() -> int:
    try:
        projects = yaml.safe_load(SETTINGS.read_text(encoding="utf-8"))["projects"]
    except Exception as error:  # noqa: BLE001 失敗の内容を出して止める
        print("監視対象の設定: failed")
        print(f"read {SETTINGS}: {error}", file=sys.stderr)
        return 1
    print("監視対象の設定: ok")
    failed = False
    for project in projects:
        local = Path(project["local_path"])
        if local.is_dir():
            print(f"{project['name']} のクローン: ok")
        else:
            print(f"{project['name']} のクローン: failed（{local} がありません）")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
