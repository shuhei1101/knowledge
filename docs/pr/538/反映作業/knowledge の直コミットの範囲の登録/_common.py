"""knowledge の直コミットの範囲の登録の反映作業で、各スクリプトが共有する固定値と API の呼び出し。"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

API = "http://127.0.0.1:8786/settings/sources"
SOURCE_ID = "knowledge"
CONFIG = "/home/shuhei2441/repo/knowledge/.claude/worktrees/develop/project-index.yaml"
SCOPE = ["/home/shuhei2441/**"]
TIMEOUT_SEC = 30


def request(method: str, url: str, body: dict | None = None) -> tuple[int, dict]:
    """端末の設定の API を呼び、HTTP の状態と JSON の本文を返す。"""
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as res:
            return res.status, json.loads(res.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8") or "{}")


def find_row(body: dict) -> dict | None:
    """端末の設定の API の応答から knowledge の行を返す。"""
    return next((row for row in body.get("sources", []) if row.get("id") == SOURCE_ID), None)
