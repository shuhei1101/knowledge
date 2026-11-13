#!/bin/sh
set -eu

# origin のタグを読めるか
if git ls-remote --tags origin 'design-schemas/*' > /dev/null 2>&1; then
  echo "origin のタグの一覧: ok"
else
  echo "origin のタグの一覧: failed"
  exit 1
fi

# origin/develop を取得できるか
if git fetch --quiet origin develop; then
  echo "origin/develop の取得: ok"
else
  echo "origin/develop の取得: failed"
  exit 1
fi
