"""画面設計書・部品設計書を持つ監視対象のプロジェクトと設計書の一覧を、プロジェクトごとの起票の内容として出す。"""

import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True
SETTINGS = Path.home() / ".config/ai-monitor/settings.yaml"
# スキーマの原本を持ち、自分の設計書を持たないプロジェクト
EXCLUDED = {"knowledge"}
FOLDERS = ("docs/screen", "docs/component")


def _root(project: dict) -> Path:
    """稼働しているブランチの worktree の直下（無ければクローンの直下）。"""
    local = Path(project["local_path"])
    worktree = local / ".claude/worktrees/develop"
    return worktree if worktree.is_dir() else local


def _designs(root: Path) -> list[str]:
    """画面設計書・部品設計書のリポジトリの直下からのパス（目次の index.yaml を除く）。"""
    found: list[str] = []
    for folder in FOLDERS:
        base = root / folder
        if base.is_dir():
            found += [p.relative_to(root).as_posix() for p in sorted(base.glob("*.yaml")) if p.name != "index.yaml"]
    return found


def main() -> int:
    # 前提確認: 引数は無しか --dry-run だけ
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--dry-run"):
        print("前提確認: failed")
        return 1
    try:
        projects = yaml.safe_load(SETTINGS.read_text(encoding="utf-8"))["projects"]
    except Exception as error:  # noqa: BLE001 失敗の内容を出して止める
        print("前提確認: failed")
        print(f"read {SETTINGS}: {error}", file=sys.stderr)
        return 1
    print("前提確認: ok")

    # 計画: プロジェクトごとに画面設計書・部品設計書を並べる
    targets = 0
    for project in projects:
        name = project["name"]
        if name in EXCLUDED:
            continue
        designs = _designs(_root(project))
        if not designs:
            print(f"{name}: skipped（画面設計書・部品設計書が無い）")
            continue
        targets += 1
        print(f"{name}: changed（{project.get('repo', '')}・{len(designs)} 件）")
        for path in designs:
            print(f"  - {path}")
    if targets == 0:
        print("前提確認: failed（起票するプロジェクトが 0 件です）")
        return 1

    # 適用は MCP create_issue で planner が行うため、スクリプトは起票の内容を出して終える
    print(f"起票するプロジェクト: {targets} 件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
