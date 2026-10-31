"""knowledge の E2E テストで共通に使う fixture。

dev-docs は端末の設定の `clone` の `.venv` の Python で、一時フォルダの端末の設定と空いているポートで起動する。
端末の設定（`~/.config/dev-docs/settings.yaml`）は読むだけで書き換えない。
"""

import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest
from ruamel.yaml import YAML

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Mapping, Sequence

# リポジトリの直下
REPO_ROOT = Path(__file__).resolve().parents[2]

# 結果の退避先と中断の合図の場所を渡す環境変数
RUN_DIR_ENV = "KNOWLEDGE_RUN_DIR"
# 起動する dev-docs のクローンを上書きする環境変数
CLONE_ENV = "KNOWLEDGE_E2E_DEV_DOCS_CLONE"
# 端末の設定の既定の場所
TERMINAL_SETTINGS = Path.home() / ".config" / "dev-docs" / "settings.yaml"

# 中断で飛ばしたテストの結果の値
NOT_RUN = "not_run"
# results.jsonl に残す理由の最大の文字数
REASON_MAX_CHARS = 2000
# dev-docs の起動を待つ秒数
SERVE_WAIT_SEC = 60
# 起動を待つ間の問い合わせの間隔
POLL_INTERVAL_SEC = 0.2
# HTTP の呼び出しを待つ秒数（書き込みは検査のスクリプトを待つ）
HTTP_TIMEOUT_SEC = 60
# 子プロセスを待つ秒数
PROCESS_WAIT_SEC = 120
MCP_HEADERS = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
}

# 一時のクローンで commit するときの作者
_GIT_IDENTITY = ("-c", "user.name=knowledge-e2e", "-c", "user.email=knowledge-e2e@example.invalid")


def pytest_addoption(parser: pytest.Parser) -> None:
    """誤実行を防ぐ `--run-e2e` を追加する。"""
    parser.addoption("--run-e2e", action="store_true", default=False, help="E2E テストを実行する")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """`--run-e2e` が無いときは E2E テストを飛ばす。"""
    if config.getoption("run_e2e", default=False):
        return
    skip = pytest.mark.skip(reason="E2E テストは --run-e2e を付けたときだけ実行する")
    for item in items:
        # E2E のフォルダのテストだけに付ける
        if "tests/e2e/" in item.nodeid:
            item.add_marker(skip)


def _run_dir() -> Path | None:
    """結果と合図を置くフォルダを返す。指定が無ければ None。"""
    value = os.environ.get(RUN_DIR_ENV, "")
    return Path(value) if value else None


def pytest_runtest_setup() -> None:
    """中断の合図ファイル（`$RUN_DIR/abort`）があれば、このテストを未実行として飛ばす。"""
    run_dir = _run_dir()
    if run_dir is not None and (run_dir / "abort").exists():
        pytest.skip(f"中断の合図（{run_dir / 'abort'}）により未実行です")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """テスト 1 件の結果が確定するたびに `$RUN_DIR/results.jsonl` へ追記する。"""
    run_dir = _run_dir()
    if run_dir is None:
        return
    # setup / teardown は失敗したとき・飛ばされたときだけ記録する（正常時は call の結果で足りる）
    if report.when != "call" and report.outcome not in ("failed", "skipped"):
        return
    reason = report.longreprtext or ""
    aborted = "中断の合図" in reason and report.outcome == "skipped"
    entry = {
        "test_id": report.nodeid,
        "phase": report.when,
        "outcome": NOT_RUN if aborted else report.outcome,
        "duration_sec": round(report.duration, 1),
        "reason": reason[-REASON_MAX_CHARS:],
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "results.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_yaml(path: Path) -> dict[str, Any]:
    """YAML のファイルを読んだ値を返す。"""
    return cast("dict[str, Any]", YAML(typ="safe").load(path.read_text(encoding="utf-8")))


def run_git(folder: Path, *args: str) -> str:
    """フォルダで git を実行し、標準出力を返す。"""
    result = subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
        ["git", *_GIT_IDENTITY, *args],  # noqa: S607 - git は PATH から引く
        cwd=folder,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=PROCESS_WAIT_SEC,
    )
    return result.stdout


def path_without_maid() -> str:
    """今の PATH から、maid を持つフォルダを除いた PATH を返す。"""
    folders = os.environ.get("PATH", "").split(os.pathsep)
    return os.pathsep.join(folder for folder in folders if not (Path(folder) / "maid").exists())


@dataclass(frozen=True)
class ToolResult:
    """MCP のツールの呼び出しの結果。"""

    is_error: bool
    text: str

    @property
    def data(self) -> dict[str, Any]:
        """本文を JSON のオブジェクトとして読んだ値を返す。"""
        return cast("dict[str, Any]", json.loads(self.text))


@dataclass(frozen=True)
class Page:
    """画面の API で開いた文書。"""

    status: int
    body: dict[str, Any]


def _read_json(request: urllib.request.Request | str) -> tuple[int, Any]:
    """HTTP で呼び、ステータスと応答の JSON を返す（4xx・5xx も本文を返す）。"""
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SEC) as response:  # noqa: S310 - 127.0.0.1 の http だけを呼ぶ
            return int(response.status), json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return int(error.code), json.loads(error.read().decode("utf-8"))


@dataclass
class Served:
    """子プロセスで動く `dev-docs serve` と、その端末の設定。"""

    process: subprocess.Popen[bytes]
    port: int
    settings: Path
    stderr_path: Path

    def sources(self) -> list[dict[str, Any]]:
        """一時フォルダの端末の設定の `sources[]` を返す。"""
        return list(load_yaml(self.settings)["sources"])

    def url(self, path: str) -> str:
        """待ち受けのアドレスに path をつなげた URL を返す。"""
        return f"http://127.0.0.1:{self.port}{path}"

    def call(self, name: str, **arguments: object) -> ToolResult:
        """文書の MCP（`/mcp/`）のツールを呼ぶ。"""
        return self._call("/mcp/", name, arguments)

    def call_admin(self, name: str, **arguments: object) -> ToolResult:
        """管理の MCP（`/_admin/mcp/`）のツールを呼ぶ。"""
        return self._call("/_admin/mcp/", name, arguments)

    def open_page(self, source: str, path: str = "") -> Page:
        """画面の API で文書を開く。path を省くと既定の文書を開く。"""
        suffix = f"/{urllib.parse.quote(path)}" if path else ""
        status, body = _read_json(self.url(f"/_api/sources/{source}/docs{suffix}"))
        return Page(status, cast("dict[str, Any]", body))

    def _call(self, path: str, name: str, arguments: Mapping[str, object]) -> ToolResult:
        """JSON-RPC の tools/call を 1 つ送信する。"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        request = urllib.request.Request(  # noqa: S310 - 127.0.0.1 の http だけを呼ぶ
            self.url(path),
            data=json.dumps(payload).encode("utf-8"),
            headers=MCP_HEADERS,
            method="POST",
        )
        _, response = _read_json(request)
        result = cast("dict[str, Any]", response["result"])
        parts = cast("list[dict[str, Any]]", result["content"])
        return ToolResult(
            is_error=bool(result.get("isError")),
            text="".join(str(part["text"]) for part in parts if part["type"] == "text"),
        )


@dataclass(frozen=True)
class SourceRow:
    """端末の設定の `sources[]` の 1 行。"""

    config: Path
    read: Sequence[str]
    write: Sequence[str]
    id: str = "knowledge"


def dev_docs_clone() -> Path:
    """起動する dev-docs のクローンを返す（環境変数か、端末の設定の `clone`）。"""
    value = os.environ.get(CLONE_ENV, "")
    if value:
        return Path(value)
    # 端末の設定が無ければ、準備が足りないことを示して止める
    if not TERMINAL_SETTINGS.exists():
        pytest.fail(
            f"{TERMINAL_SETTINGS} がありません。/dev-docs:global-setup を済ませるか、{CLONE_ENV} を渡してください",
            pytrace=False,
        )
    return Path(str(load_yaml(TERMINAL_SETTINGS)["clone"]))


def write_settings(path: Path, rows: Sequence[SourceRow]) -> None:
    """一時フォルダの端末の設定を、渡した配信元の行で書き込む。"""
    lines = [
        'version: "1"',
        f"clone: {dev_docs_clone()}",
        f"state_dir: {path.parent / 'state'}",
        "sources:" if rows else "sources: []",
    ]
    for row in rows:
        lines += [f"  - id: {row.id}", "    config:", f"      - {row.config}", "    scope:"]
        lines += ["      read:", *(f'        - "{item}"' for item in row.read)]
        lines += ["      write:", *(f'        - "{item}"' for item in row.write)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _knowledge_row(clone: Path, *, read: Sequence[str] = ("/**",)) -> SourceRow:
    """knowledge をクローンと worktree から書ける配信元の行を返す。既定は全ての作業場所から読める。"""
    return SourceRow(
        config=clone / "dev-docs.yaml",
        read=read,
        write=[str(clone), f"{clone}/.claude/worktrees/**"],
    )


def _free_port() -> int:
    """今は空いている 127.0.0.1 のポートを返す。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_until_serving(served: Served) -> None:
    """dev-docs が画面の API で応答するまで待つ。"""
    deadline = time.monotonic() + SERVE_WAIT_SEC
    while time.monotonic() < deadline:
        # 先に終わったら標準エラーを示して止める
        if served.process.poll() is not None:
            stderr = served.stderr_path.read_text(encoding="utf-8")
            message = f"dev-docs serve が先に終わった\n{stderr}"
            raise AssertionError(message)
        try:
            with urllib.request.urlopen(served.url("/_api/openapi.json"), timeout=1):  # noqa: S310 - 127.0.0.1 の http だけを呼ぶ
                return
        except OSError:
            time.sleep(POLL_INTERVAL_SEC)
    message = "dev-docs serve が待ち受けを始めなかった"
    raise AssertionError(message)


@pytest.fixture
def knowledge_clone(tmp_path: Path) -> Callable[..., Path]:
    """knowledge の HEAD を一時フォルダへクローンし、develop を踏ませて返す関数を返す。"""

    def _clone(files: Mapping[str, str] | None = None) -> Path:
        folder = tmp_path / "knowledge"
        run_git(tmp_path, "clone", "--quiet", str(REPO_ROOT), str(folder))
        run_git(folder, "checkout", "--quiet", "-B", "develop")
        # 渡したファイルで書き換え、develop に commit する
        if files:
            for relative, text in files.items():
                target = folder / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
            run_git(folder, "add", "--all")
            run_git(folder, "commit", "--quiet", "-m", "e2e の準備")
        return folder

    return _clone


@pytest.fixture
def knowledge_worktree() -> Callable[[Path], Path]:
    """knowledge のクローンに、develop から切った作業ブランチの worktree を作る関数を返す。"""

    def _create(clone: Path) -> Path:
        worktree = clone / ".claude" / "worktrees" / "e2e"
        run_git(clone, "worktree", "add", "--quiet", "-b", "feat/e2e", str(worktree))
        return worktree

    return _create


@pytest.fixture
def serve(tmp_path: Path) -> Iterator[Callable[[Sequence[SourceRow]], Served]]:
    """一時フォルダの端末の設定で `dev-docs serve` を起動し、応答するまで待つ関数を返す（終了時に止める）。"""
    started: list[Served] = []

    def _serve(rows: Sequence[SourceRow]) -> Served:
        folder = tmp_path / "dev-docs"
        folder.mkdir(exist_ok=True)
        settings = folder / "settings.yaml"
        write_settings(settings, rows)
        port = _free_port()
        stderr_path = folder / "serve.stderr"
        # 端末の DEV_DOCS_* は渡さず、一時フォルダの設定とポートだけを渡す
        env = {key: value for key, value in os.environ.items() if not key.startswith("DEV_DOCS_")}
        env |= {"DEV_DOCS_CONFIG": str(settings), "DEV_DOCS_PORT": str(port)}
        python = dev_docs_clone() / ".venv" / "bin" / "python"
        with stderr_path.open("wb") as err:
            process = subprocess.Popen(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
                [str(python), "-m", "dev_docs", "serve"],
                env=env,
                cwd=folder,
                stdout=subprocess.DEVNULL,
                stderr=err,
            )
        served = Served(process, port, settings, stderr_path)
        started.append(served)
        _wait_until_serving(served)
        return served

    yield _serve
    for served in started:
        # まだ動いていれば止める
        if served.process.poll() is None:
            served.process.terminate()
            served.process.wait(timeout=PROCESS_WAIT_SEC)


@dataclass(frozen=True)
class Registration:
    """登録の処理の結果。点検で止まったときは reload と status を持たない。"""

    check: ToolResult
    reload: ToolResult | None
    status: ToolResult | None


def _register(served: Served, path: Path, row: SourceRow) -> Registration:
    """`/dev-docs:setup` が行う処理を順に行う（点検 → 端末の設定への記載 → 読み直し → 状態の確認）。"""
    check = served.call_admin("check_project", path=str(path), format="json")
    # 点検で違反があれば端末の設定を書き換えずに止める
    if check.is_error or check.data.get("violations"):
        return Registration(check, None, None)
    write_settings(served.settings, [row])
    reload = served.call_admin("reload", format="json")
    status = served.call_admin("status", format="json")
    return Registration(check, reload, status)


def _run_check_all(folder: Path, *, without_maid: bool = False) -> subprocess.CompletedProcess[str]:
    """CI のジョブと同じコマンドで、全ての文書の検査を子プロセスとして起動する。"""
    path = path_without_maid() if without_maid else os.environ.get("PATH", "")
    return subprocess.run(
        ["uv", "run", "--frozen", "--script", "scripts/check_all.py"],  # noqa: S607 - uv は PATH から引く
        cwd=folder,
        env={**os.environ, "PATH": path},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=PROCESS_WAIT_SEC,
    )


# 配信のワークフローの、成果物を作るコマンドと、出力に YAML が無いことを確かめるコマンド
PAGES_BUILD = ("uv", "run", "--frozen", "--script", "scripts/build_pages.py", "--out", "_site")
PAGES_YAML_CHECK = "! find _site -type f \\( -name '*.yaml' -o -name '*.yml' \\) | grep ."


def _run_pages_build(folder: Path) -> subprocess.CompletedProcess[str]:
    """配信のワークフローと同じコマンドで、Pages の成果物を作るスクリプトを子プロセスとして起動する。"""
    return subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
        PAGES_BUILD,
        cwd=folder,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=PROCESS_WAIT_SEC,
    )


def _run_pages_yaml_check(folder: Path) -> subprocess.CompletedProcess[str]:
    """配信のワークフローと同じコマンドを bash で起動し、出力に YAML が無いことを確かめる。"""
    return subprocess.run(  # noqa: S603 - ワークフローと同じ固定のコマンドの行を bash に渡す
        ["bash", "-c", PAGES_YAML_CHECK],  # noqa: S607 - bash は PATH から引く
        cwd=folder,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=PROCESS_WAIT_SEC,
    )


def _page_path(clone: Path, file: Path) -> str:
    """文書のファイルを、画面の API のページの path にする（拡張子を落とした直下からのパス）。"""
    return str(file.relative_to(clone).with_suffix(""))


def _representative_pages(clone: Path) -> dict[str, str]:
    """`dev-docs.yaml` の文書の行ごとに、先頭の文書のページの path を返す。"""
    config = load_yaml(clone / "dev-docs.yaml")
    pages: dict[str, str] = {}
    for document in config["documents"]:
        files = sorted(file for pattern in document["paths"] for file in clone.glob(pattern))
        # files.yaml の行の文書は、先頭の行のファイルをページにする
        if "records" in document:
            record = load_yaml(files[0])[document["records"]][0]
            body = files[0].parent / str(record[document["body_file"]])
            pages[document["id"]] = f"{_page_path(clone, files[0])}/{_page_path(clone, body)}"
        else:
            pages[document["id"]] = _page_path(clone, files[0])
    return pages


@pytest.fixture
def knowledge_row() -> Callable[..., SourceRow]:
    """knowledge の配信元の行を作る関数を返す。"""
    return _knowledge_row


@pytest.fixture
def register() -> Callable[[Served, Path, SourceRow], Registration]:
    """`/dev-docs:setup` が行う処理を順に行う関数を返す。"""
    return _register


@pytest.fixture
def run_check_all() -> Callable[..., subprocess.CompletedProcess[str]]:
    """CI のジョブと同じコマンドで全ての文書の検査を起動する関数を返す。"""
    return _run_check_all


@pytest.fixture
def representative_pages() -> Callable[[Path], dict[str, str]]:
    """文書の行ごとの先頭の文書のページの path を返す関数を返す。"""
    return _representative_pages


@pytest.fixture
def run_pages_build() -> Callable[[Path], subprocess.CompletedProcess[str]]:
    """配信のワークフローと同じコマンドで Pages の成果物を作る関数を返す。"""
    return _run_pages_build


@pytest.fixture
def run_pages_yaml_check() -> Callable[[Path], subprocess.CompletedProcess[str]]:
    """配信のワークフローと同じコマンドで出力に YAML が無いことを確かめる関数を返す。"""
    return _run_pages_yaml_check
