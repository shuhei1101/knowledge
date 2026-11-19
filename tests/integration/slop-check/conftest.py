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

# 画面への表示を切り替える環境変数（端末の値を子プロセスへ持ち込まないよう、起動のたびに決める）
_SHOW_ADDED_ENV = "SLOP_CHECK_SHOW_ADDED"


@dataclass(frozen=True)
class Completed:
    """子プロセスの結果。"""

    exit_code: int
    stdout: str
    stderr: str


type RunHook = Callable[..., Completed]
type PluginFactory = Callable[[Sequence[Mapping[str, object]]], Path]


@pytest.fixture
def run_hook() -> RunHook:
    """標準入力・CLAUDE_PLUGIN_ROOT・SLOP_CHECK_SHOW_ADDED の値を指定してフックを起動する関数を返却する。"""

    def _start(stdin: str, plugin_root: Path, show_added: str | None = None) -> Completed:
        env = {k: v for k, v in os.environ.items() if k != _SHOW_ADDED_ENV}
        env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
        # 値を指定したときだけ子プロセスへ指定する（None は環境変数が無い端末として起動する）
        if show_added is not None:
            env[_SHOW_ADDED_ENV] = show_added
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
