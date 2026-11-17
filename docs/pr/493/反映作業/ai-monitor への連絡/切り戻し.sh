#!/bin/sh
set -eu

ME=$(gh api user --jq .login)
IDS=$(gh api repos/shuhei1101/ai-monitor/issues/3607/comments --paginate \
  --jq ".[] | select(.user.login == \"$ME\" and (.body | contains(\"design-schemas/v\")) and (.body | contains(\"#493\"))) | .id")
if [ -z "$IDS" ]; then
  echo "コメントの削除: skipped（$ME が投稿した design-schemas/v と #493 を含むコメントがありません）"
  exit 0
fi
for ID in $IDS; do
  if ! gh api -X DELETE "repos/shuhei1101/ai-monitor/issues/comments/$ID" >/dev/null; then
    echo "コメントの削除: failed"
    echo "gh api -X DELETE repos/shuhei1101/ai-monitor/issues/comments/$ID"
    exit 1
  fi
done
echo "コメントの削除: changed"
