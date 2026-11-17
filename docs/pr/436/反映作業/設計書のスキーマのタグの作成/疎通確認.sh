#!/bin/sh
set -eu

if git ls-remote --tags --refs origin 'design-schemas/*' >/dev/null 2>&1; then
  echo "origin のタグの一覧: ok"
else
  echo "origin のタグの一覧: failed"
  git ls-remote --tags --refs origin 'design-schemas/*'
  exit 1
fi
