#!/bin/sh
set -eu

git fetch --quiet origin --tags
TAG=""
for T in $(git tag -l 'design-schemas/v*'); do
  if git tag -l --format='%(contents:subject)' "$T" | grep -qF '(#493)'; then
    TAG=$T
  fi
done
if [ -z "$TAG" ]; then
  echo "メッセージに (#493) を持つタグ: failed（タグがありません）"
  exit 1
fi
COUNT=$(gh api repos/shuhei1101/ai-monitor/issues/3607/comments --paginate \
  --jq "[.[] | select((.body | contains(\"$TAG\")) and (.body | contains(\"test_files\")))] | length" | awk '{ s += $1 } END { print s + 0 }')
if [ "$COUNT" -gt 0 ]; then
  echo "ai-monitor#3607 のコメント: ok（$TAG）"
else
  echo "ai-monitor#3607 のコメント: failed"
  gh api repos/shuhei1101/ai-monitor/issues/3607/comments --paginate --jq '.[-1].body'
  exit 1
fi
