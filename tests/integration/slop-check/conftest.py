"""slop-check の結合テストで共通に使う fixture。フックのスクリプトを子プロセスとして起動する。"""

import json
import os
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import pytest

# フックのスクリプト（hooks.json と同じく python3 で起動する）
HOOK = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "slop-check"
    / "hooks"
    / "post-tool-use"
    / "slop_check.py"
)

# 子プロセスを待つ上限の秒数
_WAIT_SEC = 30


@dataclass(frozen=True)
class Completed:
    """子プロセスの結果。"""

    exit_code: int
    stdout: str
    stderr: str


type RunHook = Callable[[str, Path], Completed]
type PluginFactory = Callable[[Sequence[Mapping[str, object]]], Path]


@pytest.fixture
def run_hook() -> RunHook:
    """標準入力と CLAUDE_PLUGIN_ROOT を指定してフックを起動する関数を返す。"""

    def _start(stdin: str, plugin_root: Path) -> Completed:
        env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(plugin_root)}
        result = subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
            ["python3", str(HOOK)],  # noqa: S607 - hooks.json と同じく PATH の python3 で起動する
            input=stdin.encode("utf-8"),
            capture_output=True,
            env=env,
            timeout=_WAIT_SEC,
            check=False,
        )
        return Completed(
            exit_code=result.returncode,
            stdout=result.stdout.decode("utf-8"),
            stderr=result.stderr.decode("utf-8"),
        )

    return _start


@pytest.fixture
def plugin_factory(tmp_path: Path) -> PluginFactory:
    """渡した行を持つ対応表のコピーを置いたプラグインのフォルダを作る関数を返す。"""

    def _create(entries: Sequence[Mapping[str, object]]) -> Path:
        root = tmp_path / "plugin"
        folder = root / "hooks" / "post-tool-use"
        folder.mkdir(parents=True)
        (folder / "word-list-ai-slop.json").write_text(
            json.dumps({"entries": list(entries)}, ensure_ascii=False), encoding="utf-8"
        )
        return root

    return _create
