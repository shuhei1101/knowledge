"""scripts/ の結合テストで共通に使う fixture。入口のスクリプトを子プロセスとして起動する。"""

import os
import subprocess
import sys
import textwrap
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import pytest

# リポジトリの直下と、入口のスクリプトの置き場所
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "scripts"

# 子プロセスを待つ上限の秒数。スクリプトの処理時間の上限（20 秒）に起動の時間を加えた値
_WAIT_SEC = 60

# 打ち切られるまで返らない maid の差し替えの本体
_HANGING_MAID = textwrap.dedent(
    """\
    #!{python}
    import time

    time.sleep(600)
    """
)

# 規約の文書のスキーマが $ref で指す共通のスキーマ
COMMON_SCHEMA = textwrap.dedent(
    """\
    $schema: https://json-schema.org/draft/2020-12/schema
    title: 共通
    $defs:
      metadata:
        type: object
        required:
          - id
          - kind
          - name
          - description
        properties:
          id:
            type: string
          kind:
            type: string
          name:
            type: string
          description:
            type: string
          items:
            type: array
    """
)

# 規約の文書のスキーマ
RULE_SCHEMA = textwrap.dedent(
    """\
    $schema: https://json-schema.org/draft/2020-12/schema
    title: 規約
    allOf:
      - $ref: common.schema.yaml#/$defs/metadata
    properties:
      kind:
        const: rule
    """
)

# 規約の文書を docs/rule/ から引き、文書の違反の検査も当てる dev-docs.yaml
DEV_DOCS_YAML = textwrap.dedent(
    """\
    version: "3"
    name: knowledge
    validators:
      - id: knowledge-checks
        run: [uv, run, --frozen, --script, scripts/knowledge_checks.py]
        on: [write]
    documents:
      - id: rule
        paths:
          - docs/rule/*.yaml
        schema: schemas/rule.schema.yaml
        validators:
          - knowledge-checks
    """
)


@dataclass(frozen=True)
class Completed:
    """子プロセスの結果。"""

    exit_code: int
    stdout: str
    stderr: str
    elapsed_sec: float


type RunScript = Callable[..., Completed]
type RunChecksWithLimit = Callable[[Path, str, float], Completed]
type RepoFactory = Callable[[Mapping[str, str]], Path]


def _path_without_maid() -> str:
    """今の PATH から、maid を持つフォルダを除いた PATH を返す。"""
    folders = os.environ.get("PATH", "").split(os.pathsep)
    return os.pathsep.join(folder for folder in folders if not (Path(folder) / "maid").exists())


def _run(command: Sequence[str], cwd: Path, stdin: str, path: str) -> Completed:
    """コマンドを子プロセスで起動し、終了を待って結果を返す。"""
    env = {**os.environ, "PATH": path}
    started = time.monotonic()
    result = subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
        command,
        cwd=cwd,
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
        elapsed_sec=time.monotonic() - started,
    )


@pytest.fixture
def run_script() -> RunScript:
    """入口のスクリプトを dev-docs・CI と同じ `uv run --frozen --script` で起動する関数を返す。"""

    def _start(
        name: str,
        cwd: Path,
        stdin: str = "",
        *,
        without_maid: bool = False,
        args: Sequence[str] = (),
        path_prefix: Path | None = None,
    ) -> Completed:
        # maid を外すときは、maid を持つフォルダを PATH から除く
        path = _path_without_maid() if without_maid else os.environ.get("PATH", "")
        # 差し替えのコマンドを置いたフォルダは PATH の先頭に置く
        if path_prefix is not None:
            path = os.pathsep.join([str(path_prefix), path])
        command = ["uv", "run", "--frozen", "--script", str(SCRIPTS / f"{name}.py"), *args]
        return _run(command, cwd, stdin, path)

    return _start


@pytest.fixture
def run_checks_with_limit(tmp_path: Path) -> RunChecksWithLimit:
    """処理時間の上限を引数で差し替え、打ち切りまで返らない maid で文書の違反の検査を起動する関数を返す。"""
    folder = tmp_path / "hanging-maid-bin"
    folder.mkdir()
    maid = folder / "maid"
    maid.write_text(_HANGING_MAID.format(python=sys.executable), encoding="utf-8")
    maid.chmod(0o755)

    def _start(cwd: Path, stdin: str, limit_sec: float) -> Completed:
        # 入口の main を、上限の引数を渡して子プロセスの中で呼ぶ
        code = (
            f"import sys; sys.path.insert(0, {str(SCRIPTS)!r}); import knowledge_checks; "
            f"sys.exit(knowledge_checks.main([], limit_sec={limit_sec!r}))"
        )
        path = os.pathsep.join([str(folder), _path_without_maid()])
        return _run([sys.executable, "-c", code], cwd, stdin, path)

    return _start


@pytest.fixture
def repo_factory(tmp_path: Path) -> RepoFactory:
    """schemas/ と dev-docs.yaml と、渡した文書を持つリポジトリの直下を作る関数を返す。"""

    def _create(files: Mapping[str, str]) -> Path:
        root = tmp_path / "repo"
        (root / "schemas").mkdir(parents=True)
        (root / "docs").mkdir()
        (root / "schemas" / "common.schema.yaml").write_text(COMMON_SCHEMA, encoding="utf-8")
        (root / "schemas" / "rule.schema.yaml").write_text(RULE_SCHEMA, encoding="utf-8")
        (root / "dev-docs.yaml").write_text(DEV_DOCS_YAML, encoding="utf-8")
        # 渡したファイルで既定のファイルを上書きできる
        for relative, text in files.items():
            file = root / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(text, encoding="utf-8")
        return root

    return _create
