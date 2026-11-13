#!/bin/sh
set -eu

API=repos/shuhei1101/knowledge/environments/github-pages/deployment-branch-policies

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi
if ! NAMES=$(gh api "$API" --jq '.branch_policies[].name' 2>&1); then
  echo "前提確認: failed"
  echo "$NAMES"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
echo "今の配信を許すブランチ: $(echo "$NAMES" | tr '\n' ' ')"
if echo "$NAMES" | grep -qx 'develop'; then
  echo "develop の追加: skipped"
  exit 0
fi
echo "追加する配信を許すブランチ: develop（type: branch）"
if [ "${1:-}" = "--dry-run" ]; then
  echo "develop の追加: changed"
  exit 0
fi

# 適用
gh api -X POST "$API" -f name=develop -f type=branch > /dev/null
echo "develop の追加: changed"
