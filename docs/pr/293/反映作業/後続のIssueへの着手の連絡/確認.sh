#!/bin/sh
set -eu

REPO=shuhei1101/ai-monitor
ISSUE=3184
PR_URL=https://github.com/shuhei1101/knowledge/pull/293
LABEL=確認:task-planner
RC=0

if gh issue view "$ISSUE" -R "$REPO" --json comments -q '.comments[].body' | grep -qF "$PR_URL"; then
  echo "着手の連絡のコメント: ok"
else
  echo "着手の連絡のコメント: failed（$PR_URL を含むコメントが無い）"
  RC=1
fi
LABELS=$(gh issue view "$ISSUE" -R "$REPO" --json labels -q '.labels[].name' | tr '\n' ' ')
if printf '%s\n' $LABELS | grep -qxF "$LABEL"; then
  echo "確認ラベルの付与: ok"
else
  echo "確認ラベルの付与: failed（今のラベル: $LABELS）"
  RC=1
fi
exit $RC
