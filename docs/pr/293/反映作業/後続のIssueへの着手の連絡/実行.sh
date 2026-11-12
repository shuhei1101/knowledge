#!/bin/sh
set -eu

REPO=shuhei1101/ai-monitor
ISSUE=3184
PR_URL=https://github.com/shuhei1101/knowledge/pull/293
LABEL=確認:task-planner

# 前提確認
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed"
  exit 1
fi
if [ "$(gh pr view 293 -R shuhei1101/knowledge --json state -q .state)" != "MERGED" ]; then
  echo "前提確認: failed"
  echo "gh pr view 293 -R shuhei1101/knowledge --json state: MERGED でない"
  exit 1
fi
if [ "$(gh issue view "$ISSUE" -R "$REPO" --json state -q .state)" != "OPEN" ]; then
  echo "前提確認: failed"
  echo "gh issue view $ISSUE -R $REPO --json state: OPEN でない"
  exit 1
fi
echo "前提確認: ok"

BODY=$(cat <<BODY_EOF
> from: @planner
> to: @task-planner

knowledge の判定フローチャート『再利用と新規作成の選び方』（ID: \`flowchart-reuse-choice\`、パス: \`docs/flowchart/flowchart-reuse-choice.yaml\`）が develop へ入りました（$PR_URL）。
この Issue に着手できます。
BODY_EOF
)

# 計画（--dry-run もここを通る）
if gh issue view "$ISSUE" -R "$REPO" --json comments -q '.comments[].body' | grep -qF "$PR_URL"; then
  COMMENT=skipped
else
  COMMENT=changed
  echo "--- /dev/null"
  echo "+++ $REPO#$ISSUE のコメント"
  printf '%s\n' "$BODY" | sed 's/^/+/'
fi
if gh issue view "$ISSUE" -R "$REPO" --json labels -q '.labels[].name' | grep -qxF "$LABEL"; then
  LABELING=skipped
else
  LABELING=changed
  echo "+ $REPO#$ISSUE のラベル: $LABEL"
fi
if [ "${1:-}" = "--dry-run" ]; then
  echo "着手の連絡のコメント: $COMMENT"
  echo "確認ラベルの付与: $LABELING"
  exit 0
fi

# 適用
if [ "$COMMENT" = changed ]; then
  if ! gh issue comment "$ISSUE" -R "$REPO" --body "$BODY" >/dev/null 2>err.tmp; then
    echo "着手の連絡のコメント: failed"
    echo "gh issue comment $ISSUE -R $REPO"
    cat err.tmp; rm -f err.tmp
    exit 1
  fi
  rm -f err.tmp
fi
echo "着手の連絡のコメント: $COMMENT"
if [ "$LABELING" = changed ]; then
  if ! gh issue edit "$ISSUE" -R "$REPO" --add-label "$LABEL" >/dev/null 2>err.tmp; then
    echo "確認ラベルの付与: failed"
    echo "gh issue edit $ISSUE -R $REPO --add-label $LABEL"
    cat err.tmp; rm -f err.tmp
    exit 1
  fi
  rm -f err.tmp
fi
echo "確認ラベルの付与: $LABELING"
