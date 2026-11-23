"""project-index の管理の MCP（http://127.0.0.1:8786/_admin/mcp）を呼ぶ共通の処理。"""

import json
import os
import subprocess
import time
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8786/_admin/mcp"
CLONE = "/home/shuhei2441/repo/project-index/.claude/worktrees/develop"
TIMEOUT_SEC = 10


def _post(body: dict, session: str | None) -> tuple[dict | None, str | None]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session:
        headers["Mcp-Session-Id"] = session
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as res:
        sid = res.headers.get("Mcp-Session-Id") or session
        text = res.read().decode()
    if not text.strip():
        return None, sid
    if text.lstrip().startswith("{"):
        return json.loads(text), sid
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip()), sid
    return None, sid


def call_tool(name: str, arguments: dict) -> dict:
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
    _, sid = _post(init, None)
    _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    res, _ = _post(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}},
        sid,
    )
    if res is None or "result" not in res:
        raise RuntimeError(f"{name} の応答が不正: {res}")
    result = res["result"]
    if result.get("isError"):
        raise RuntimeError(f"{name} がエラーを返した: {result}")
    if "structuredContent" in result:
        return result["structuredContent"]
    return json.loads(result["content"][0]["text"])


def status() -> dict:
    return call_tool("status", {"format": "json"})


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
        return False, str(e)[:300]
    bad = [v for v in res.get("violations", []) if str(v.get("path", "")).startswith("direct_commit")]
    if bad:
        return False, json.dumps(bad, ensure_ascii=False)[:300]
    return True, "direct_commit の違反なし"


def wait_loaded(tries: int = 30, interval: float = 2.0) -> dict:
    """再起動の後、status が返り loading が false になるまで待つ。"""
    last: Exception | None = None
    for _ in range(tries):
        try:
            st = status()
            if not st.get("loading"):
                return st
        except (urllib.error.URLError, OSError, RuntimeError) as e:
            last = e
        time.sleep(interval)
    raise RuntimeError(f"status が読み込みを終えない: {last}")
