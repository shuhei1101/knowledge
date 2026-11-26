#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/screen.schema.yaml" 2>/dev/null | grep -q '^        count_limit:'; then
  echo "最新のタグ $LATEST の画面設計の count_limit: ok"
else
  echo "最新のタグ $LATEST の画面設計の count_limit: failed"
  exit 1
fi
