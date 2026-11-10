#!/bin/sh
set -eu

# origin のタグを読めるか
if git ls-remote --tags origin 'design-schemas/*' > /dev/null 2>&1; then
  echo "origin のタグの一覧: ok"
else
  echo "origin のタグの一覧: failed"
  exit 1
fi

# origin/develop のモジュール構成のスキーマを読めるか
git fetch --quiet origin develop
if git show origin/develop:schemas/design/module.schema.yaml > /dev/null 2>&1; then
  echo "origin/develop の schemas/design/module.schema.yaml: ok"
else
  echo "origin/develop の schemas/design/module.schema.yaml: failed"
  exit 1
fi
