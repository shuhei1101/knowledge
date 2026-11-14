#!/bin/sh
set -eu

# shuhei1101/ai-monitor#3430 を読めるか
if gh pr view 3430 --repo shuhei1101/ai-monitor --json state > /dev/null 2>&1; then
  echo "shuhei1101/ai-monitor#3430 の取得: ok"
else
  echo "shuhei1101/ai-monitor#3430 の取得: failed"
  gh pr view 3430 --repo shuhei1101/ai-monitor --json state || true
  exit 1
fi

# origin のタグを読めるか
if git fetch --quiet origin --tags; then
  echo "origin のタグの取得: ok"
else
  echo "origin のタグの取得: failed"
  exit 1
fi
