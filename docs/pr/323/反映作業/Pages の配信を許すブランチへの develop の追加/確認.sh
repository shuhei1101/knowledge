#!/bin/sh
set -eu

NAMES=$(gh api repos/shuhei1101/knowledge/environments/github-pages/deployment-branch-policies --jq '.branch_policies[].name')
echo "配信を許すブランチ: $(echo "$NAMES" | tr '\n' ' ')"
if echo "$NAMES" | grep -qx 'develop'; then
  echo "develop の配信の許可: ok"
else
  echo "develop の配信の許可: failed"
  exit 1
fi
