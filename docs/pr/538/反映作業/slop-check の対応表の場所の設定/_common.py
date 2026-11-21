"""slop-check の対応表の場所の設定の反映作業で、各スクリプトが共有する固定値。"""

from __future__ import annotations

from pathlib import Path

ENV_KEY = "SLOP_CHECK_WORD_LIST"
VALUE = "/home/shuhei2441/repo/knowledge/.claude/worktrees/develop/plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json"
# slop-check を入れたアカウントの設定フォルダごとのユーザースコープの settings.json
SETTINGS = [
    Path("/home/shuhei2441/.claude/settings.json"),
    Path("/home/shuhei2441/.claude-dev/settings.json"),
    Path("/home/shuhei2441/.claude-dev1/settings.json"),
    Path("/home/shuhei2441/.claude-sub/settings.json"),
    Path("/home/shuhei2441/.claude-sub2/settings.json"),
    Path("/home/shuhei2441/.claude-sub3/settings.json"),
    Path("/home/shuhei2441/.claude-sub4/settings.json"),
    Path("/home/shuhei2441/.claude-sub5/settings.json"),
    Path("/home/shuhei2441/.claude-sub6/settings.json"),
    Path("/home/shuhei2441/.claude-sub7/settings.json"),
]
