#!/bin/sh
set -eu

# origin のタグを読めるか
if git ls-remote --tags origin 'design-schemas/*' > /dev/null 2>&1; then
  echo "origin のタグの一覧: ok"
else
  echo "origin のタグの一覧: failed"
  exit 1
fi

# origin/develop の共通の型のスキーマを読めるか
git fetch --quiet origin develop
if git show origin/develop:schemas/design/common.schema.yaml > /dev/null 2>&1; then
  echo "origin/develop の schemas/design/common.schema.yaml: ok"
else
  echo "origin/develop の schemas/design/common.schema.yaml: failed"
  exit 1
fi
