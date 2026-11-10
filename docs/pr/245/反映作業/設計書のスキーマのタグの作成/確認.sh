#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/module.schema.yaml" | grep -qF '1 テストファイル、規約『V字モデル』'; then
  echo "最新の design-schemas のタグ $LATEST の test_files の description: ok"
else
  echo "最新の design-schemas のタグ $LATEST の test_files の description: failed"
  exit 1
fi
