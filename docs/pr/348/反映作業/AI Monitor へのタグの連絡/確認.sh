#!/bin/sh
set -eu

REPO=shuhei1101/ai-monitor
NUMBER=3430
MARKER='(shuhei1101/knowledge#348)'

git fetch --quiet origin --tags
TAG=""
for T in $(git tag -l 'design-schemas/v*' --sort=-v:refname); do
  if git tag -l --format='%(contents:subject)' "$T" | grep -qF '(#348)'; then
    TAG=$T
    break
  fi
done
if [ -z "$TAG" ]; then
  echo "メッセージに (#348) を持つタグ: failed（ありません）"
  exit 1
fi
POSTED_AT=$(gh api "repos/$REPO/issues/$NUMBER/comments" --paginate -q ".[] | select(.body | contains(\"$MARKER\")) | select(.body | contains(\"$TAG\")) | .created_at" | head -n 1)
if [ -z "$POSTED_AT" ]; then
  echo "$REPO#$NUMBER の会話欄の $TAG の記載: failed"
  exit 1
fi
echo "$REPO#$NUMBER の会話欄の $TAG の記載: ok（$POSTED_AT）"
# 付けた 確認:planner は AI Monitor の planner が起動して除外するため、記載したコメント以後の付与のイベントで確認する
LABELED_AT=$(gh api "repos/$REPO/issues/$NUMBER/events" --paginate -q ".[] | select(.event == \"labeled\" and .label.name == \"確認:planner\" and .created_at >= \"$POSTED_AT\") | .created_at" | head -n 1)
if [ -n "$LABELED_AT" ]; then
  echo "$REPO#$NUMBER への 確認:planner の付与: ok（$LABELED_AT）"
else
  echo "$REPO#$NUMBER への 確認:planner の付与: failed（$POSTED_AT 以後の付与のイベントがありません）"
  exit 1
fi
