#!/bin/sh
set -eu

API=repos/shuhei1101/knowledge/environments/github-pages/deployment-branch-policies
ID=$(gh api "$API" --jq '.branch_policies[] | select(.name == "develop" and .type == "branch") | .id')
if [ -z "$ID" ]; then
  echo "develop の削除: skipped（develop の配信の許可がありません）"
  exit 0
fi
gh api -X DELETE "$API/$ID"
echo "develop の削除: changed"
