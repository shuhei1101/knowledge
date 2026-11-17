#!/bin/sh
set -eu

ME=$(gh api user --jq .login)
IDS=$(gh api repos/shuhei1101/mdmark/issues/290/comments --paginate \
  --jq ".[] | select(.user.login == \"$ME\" and (.body | contains(\"design-schemas/v9.1.0\")) and (.body | contains(\"#436\"))) | .id")
if [ -z "$IDS" ]; then
  echo "削除するコメント: failed"
  echo "$ME が投稿した design-schemas/v9.1.0 と #436 を含むコメントがありません"
  exit 1
fi
for ID in $IDS; do
  if ! gh api -X DELETE "repos/shuhei1101/mdmark/issues/comments/$ID" >/dev/null; then
    echo "コメントの削除: failed"
    echo "gh api -X DELETE repos/shuhei1101/mdmark/issues/comments/$ID"
    exit 1
  fi
done
echo "コメントの削除: changed"
