#!/bin/sh
set -eu

# shuhei1101/alias-inject#107 を読めるか
if gh issue view 107 --repo shuhei1101/alias-inject --json state > /dev/null 2>&1; then
  echo "shuhei1101/alias-inject#107 の取得: ok"
else
  echo "shuhei1101/alias-inject#107 の取得: failed"
  exit 1
fi
