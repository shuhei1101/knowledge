#!/bin/sh
set -eu

TAG=design-schemas/v8.3.0
if gh issue view 107 --repo shuhei1101/alias-inject --json comments -q '.comments[].body' | grep -qF "$TAG"; then
  echo "shuhei1101/alias-inject#107 の $TAG を記載したコメント: ok"
else
  echo "shuhei1101/alias-inject#107 の $TAG を記載したコメント: failed"
  exit 1
fi
