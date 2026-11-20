"""ネットミームの配信元の登録の反映作業で、各スクリプトが共有する固定値と API の呼び出し。"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

API = "http://127.0.0.1:8786/settings/sources"
SETTINGS = Path.home() / ".config" / "project-index" / "settings.yaml"
SOURCE_ID = "knowledge-memes"
CONFIG = "/home/shuhei2441/repo/knowledge/.claude/worktrees/develop/memes/project-index.yaml"
ROW = {
    "id": SOURCE_ID,
    "config": [CONFIG],
    "scope": {
        "read": [
            "/home/shuhei2441/repo/knowledge/**",
            "/mnt/c/Users/shuhe/repo",
            "/home/shuhei2441/repo",
            "/mnt/c/Users/shuhe/repo/tmp/*",
            "/home/shuhei2441/repo/tmp/*",
        ],
        "write": [
            "/home/shuhei2441/repo/knowledge",
            "/home/shuhei2441/repo/knowledge/.claude/worktrees/**",
        ],
    },
    "direct_commit": {"scope": ["/home/shuhei2441/**"]},
}
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
