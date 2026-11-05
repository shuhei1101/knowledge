#!/bin/sh
set -eu

REPO=shuhei1101/ai-monitor
ISSUE=2705

# close されていて、#163 への統合のコメントがあるか
STATE=$(gh issue view "$ISSUE" -R "$REPO" --json state -q .state)
MERGED=$(gh issue view "$ISSUE" -R "$REPO" --json comments -q '[.comments[].body | select(contains("shuhei1101/knowledge#163"))] | length')
echo "$REPO#$ISSUE: state=$STATE 統合のコメント=$MERGED 件"
if [ "$STATE" = "CLOSED" ] && [ "$MERGED" -ge 1 ]; then
  echo "統合と close: ok"
else
  echo "統合と close: failed"
  exit 1
fi
