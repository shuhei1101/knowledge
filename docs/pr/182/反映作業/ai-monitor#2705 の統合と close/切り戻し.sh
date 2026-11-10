#!/bin/sh
set -eu

REPO=shuhei1101/ai-monitor
ISSUE=2705

# Issue を開き直す（統合のコメントは経緯として残す）
STATE=$(gh issue view "$ISSUE" -R "$REPO" --json state -q .state)
if [ "$STATE" = "OPEN" ]; then
  echo "Issue の再オープン: skipped"
  exit 0
fi
gh issue reopen "$ISSUE" -R "$REPO" >/dev/null
echo "Issue の再オープン: changed"
