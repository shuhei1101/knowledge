"""project-index の管理の MCP（http://127.0.0.1:8786/_admin/mcp）を呼ぶ共通の処理。"""

import json
import os
import random
import subprocess
import time
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8786/_admin/mcp"
CLONE = "/home/shuhei2441/repo/project-index/.claude/worktrees/develop"

# 値の導出（規約『資源の値の決め方』。元の値は project-index の非機能要件 NFR-1）
# - 1 回の要求の打ち切り: 文書の MCP の応答の上限 48 秒（NFR-1『文書の MCP の応答の上限』）。サーバーはこの時間までに返却する
# - status の打ち切り: status は配信元の読み込みを待たずに答えるため、作業範囲の外の配信元の検索の所要時間の決定値 10 秒（NFR-1）を上限にする
# - リトライ: 一時的な通信エラー（接続の失敗・タイムアウト・HTTP 5xx）だけを 3 回まで、指数バックオフ（1・2 秒）+ ジッター 0〜1 秒
# - 再起動の後の待ち: 待ち受けまでを待つ上限 60 秒（NFR-1『起動から接続を受け付けるまでの時間』の外部の上限）+ 配信元の読み込み 14.5 秒
#   （NFR-1『同時に読み込む行の数』の 14 件の計測）の合計 74.5 秒に、余裕 50% を加えた 112 秒を切り上げて 120 秒。2 秒おきに 60 回
REQUEST_TIMEOUT_SEC = 48
STATUS_TIMEOUT_SEC = 10
RETRY_ATTEMPTS = 3
RETRY_BASE_SEC = 1.0
LOAD_WAIT_TRIES = 60
LOAD_WAIT_INTERVAL_SEC = 2.0


class TransientError(Exception):
    """接続の失敗・タイムアウト・HTTP 5xx。"""


def _post(body: dict, session: str | None, timeout: float) -> tuple[dict | None, str | None]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session:
        headers["Mcp-Session-Id"] = session
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            sid = res.headers.get("Mcp-Session-Id") or session
            text = res.read().decode()
    except urllib.error.HTTPError as e:
        if e.code >= 500:
            raise TransientError(f"HTTP {e.code}") from e
        raise
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        raise TransientError(str(e)) from e
    if not text.strip():
        return None, sid
    if text.lstrip().startswith("{"):
        return json.loads(text), sid
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip()), sid
    return None, sid


def _call_once(name: str, arguments: dict, timeout: float) -> dict:
    """ツールを 1 回呼び、structuredContent か本文の JSON を返す。"""
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "reflection-script", "version": "1"},
        },
    }
    _, sid = _post(init, None, timeout)
    _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid, timeout)
    res, _ = _post(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}},
        sid,
        timeout,
    )
    if res is None or "result" not in res:
        raise RuntimeError(f"{name} の応答が不正: {res}")
    result = res["result"]
    if result.get("isError"):
        raise RuntimeError(f"{name} がエラーを返した: {result}")
    if "structuredContent" in result:
        return result["structuredContent"]
    return json.loads(result["content"][0]["text"])


def call_tool(name: str, arguments: dict, timeout: float = REQUEST_TIMEOUT_SEC) -> dict:
    """読み取りのツールを、一時的な通信エラーのときだけ上限つきで再試行して呼ぶ。"""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            return _call_once(name, arguments, timeout)
        except TransientError:
            if attempt == RETRY_ATTEMPTS - 1:
                raise
            time.sleep(RETRY_BASE_SEC * (2**attempt) + random.uniform(0, 1))
    raise AssertionError("unreachable")


def restart(applied) -> str:
    """restart を呼ぶ。冪等でないため、再試行の前に applied() で適用済みかを判定し直す。"""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            _call_once("restart", {}, REQUEST_TIMEOUT_SEC)
            return "changed"
        except TransientError:
            if attempt == RETRY_ATTEMPTS - 1:
                raise
            time.sleep(RETRY_BASE_SEC * (2**attempt) + random.uniform(0, 1))
            try:
                wait_loaded()
                if applied():
                    return "changed"
            except (TransientError, RuntimeError):
                pass
    raise AssertionError("unreachable")


def status() -> dict:
    return call_tool("status", {"format": "json"}, STATUS_TIMEOUT_SEC)


KNOWLEDGE = "/home/shuhei2441/repo/knowledge/.claude/worktrees/develop"
OLD_KINDS = "  kinds: [knowhow, word-list, terms]\n"
PROBE_KINDS = "  kinds: [knowhow, word-list, terms, {id: skills, body: false}]\n"
REQUIRED_COMMIT = "f3c4bcd"


def clone_has_required_commit() -> bool:
    """クローンが body: false に対応した commit を含むか。"""
    r = subprocess.run(
        ["git", "-C", CLONE, "merge-base", "--is-ancestor", REQUIRED_COMMIT, "HEAD"], capture_output=True
    )
    return r.returncode == 0


def accepts_body_false() -> tuple[bool, str]:
    """動いているサーバーが direct_commit.kinds[] の {id, body: false} を受け付けるか。

    knowledge の develop の設定に {id: skills, body: false} を加えた中身を check_project に渡して確かめる。
    """
    with open(os.path.join(KNOWLEDGE, "project-index.yaml"), encoding="utf-8") as f:
        text = f.read()
    probe = text.replace(OLD_KINDS, PROBE_KINDS) if OLD_KINDS in text else text
    try:
        res = call_tool("check_project", {"path": KNOWLEDGE, "config": probe, "format": "json"})
    except RuntimeError as e:
        # 古いコードは {id, body: false} の検証でツールのエラーを返す
        return False, str(e)[:300]
    bad = [v for v in res.get("violations", []) if str(v.get("path", "")).startswith("direct_commit")]
    if bad:
        return False, json.dumps(bad, ensure_ascii=False)[:300]
    return True, "direct_commit の違反なし"


def wait_loaded() -> dict:
    """再起動の後、status が返り loading が false になるまで待つ。"""
    last: Exception | None = None
    for _ in range(LOAD_WAIT_TRIES):
        try:
            st = _call_once("status", {"format": "json"}, STATUS_TIMEOUT_SEC)
            if not st.get("loading"):
                return st
        except (TransientError, RuntimeError, OSError) as e:
            last = e
        time.sleep(LOAD_WAIT_INTERVAL_SEC)
    raise RuntimeError(f"status が読み込みを終えない: {last}")
