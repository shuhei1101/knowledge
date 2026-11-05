#!/bin/sh
set -eu

# origin へ読み取りだけでつながるか
if git ls-remote --exit-code origin refs/heads/develop >/dev/null 2>&1; then
  echo "origin の develop: ok"
else
  echo "origin の develop: failed"
  exit 1
fi
# ai-monitor#2705 を読み取れるか
if gh issue view 2705 -R shuhei1101/ai-monitor --json state >/dev/null 2>&1; then
  echo "ai-monitor#2705: ok"
else
  echo "ai-monitor#2705: failed"
  exit 1
fi
