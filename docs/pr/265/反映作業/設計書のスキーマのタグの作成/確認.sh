#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git cat-file -e "$LATEST:schemas/design/layout.schema.yaml" 2>/dev/null; then
  echo "最新の design-schemas のタグ $LATEST の schemas/design/layout.schema.yaml: ok"
else
  echo "最新の design-schemas のタグ $LATEST の schemas/design/layout.schema.yaml: failed"
  exit 1
fi
