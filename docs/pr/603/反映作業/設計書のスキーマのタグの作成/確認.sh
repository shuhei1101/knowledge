#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/screen.schema.yaml" 2>/dev/null | grep -q '^          - table_column$'; then
  echo "最新のタグ $LATEST の画面設計の要素の kind の enum: ok"
else
  echo "最新のタグ $LATEST の画面設計の要素の kind の enum: failed"
  exit 1
fi
