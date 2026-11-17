#!/bin/sh
set -eu

if gh api repos/shuhei1101/mdmark/issues/290/comments --paginate --jq '.[].body' | grep -q 'design-schemas/v9.1.0' \
  && gh api repos/shuhei1101/mdmark/issues/290/comments --paginate --jq '.[].body' | grep -q 'test_files'; then
  echo "mdmark#290 のコメント: ok"
else
  echo "mdmark#290 のコメント: failed"
  gh api repos/shuhei1101/mdmark/issues/290/comments --paginate --jq '.[-1].body'
  exit 1
fi
