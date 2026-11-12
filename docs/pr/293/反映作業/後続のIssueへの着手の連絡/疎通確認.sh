#!/bin/sh
set -eu

if gh issue view 3184 -R shuhei1101/ai-monitor --json state >/dev/null 2>err.tmp; then
  echo "shuhei1101/ai-monitor#3184 の参照: ok"
else
  echo "shuhei1101/ai-monitor#3184 の参照: failed"
  echo "gh issue view 3184 -R shuhei1101/ai-monitor --json state"
  cat err.tmp; rm -f err.tmp
  exit 1
fi
rm -f err.tmp
if gh pr view 293 -R shuhei1101/knowledge --json state >/dev/null 2>err.tmp; then
  echo "shuhei1101/knowledge#293 の参照: ok"
else
  echo "shuhei1101/knowledge#293 の参照: failed"
  echo "gh pr view 293 -R shuhei1101/knowledge --json state"
  cat err.tmp; rm -f err.tmp
  exit 1
fi
rm -f err.tmp
