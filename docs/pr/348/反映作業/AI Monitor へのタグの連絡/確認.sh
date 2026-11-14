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
STATUS=0
POSTED=$(gh api "repos/$REPO/issues/$NUMBER/comments" --paginate -q ".[] | select(.body | contains(\"$MARKER\")) | select(.body | contains(\"$TAG\")) | .id" | head -n 1)
if [ -n "$POSTED" ]; then
  echo "$REPO#$NUMBER の会話欄の $TAG の記載: ok"
else
  echo "$REPO#$NUMBER の会話欄の $TAG の記載: failed"
  STATUS=1
fi
# 付けた 確認:planner は AI Monitor の planner が起動して外すため、記載より後に付いた事実をラベルの付与のイベントで確かめる
if gh api "repos/$REPO/issues/$NUMBER/events" --paginate -q '.[] | select(.event == "labeled") | .label.name' | grep -qxF '確認:planner'; then
  echo "$REPO#$NUMBER への 確認:planner の付与: ok"
else
  echo "$REPO#$NUMBER への 確認:planner の付与: failed"
  STATUS=1
fi
exit $STATUS
