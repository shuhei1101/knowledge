#!/bin/sh
set -eu

if gh api repos/shuhei1101/mdmark/issues/290 --jq .number >/dev/null 2>&1; then
  echo "shuhei1101/mdmark#290: ok"
else
  echo "shuhei1101/mdmark#290: failed"
  gh api repos/shuhei1101/mdmark/issues/290 --jq .number
  exit 1
fi

if git ls-remote --tags --refs origin 'design-schemas/*' >/dev/null 2>&1; then
  echo "origin のタグの一覧: ok"
else
  echo "origin のタグの一覧: failed"
  git ls-remote --tags --refs origin 'design-schemas/*'
  exit 1
fi
