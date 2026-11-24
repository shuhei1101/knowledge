#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/screen.schema.yaml" 2>/dev/null | grep -q '^        overflow:'; then
  echo "最新のタグ $LATEST の画面設計の overflow: ok"
else
  echo "最新のタグ $LATEST の画面設計の overflow: failed"
  exit 1
fi
