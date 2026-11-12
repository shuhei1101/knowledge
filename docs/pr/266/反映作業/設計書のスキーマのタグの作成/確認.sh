#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/meta.schema.yaml" 2>/dev/null | grep -q '^  x-used-by:'; then
  echo "最新の design-schemas のタグ $LATEST の schemas/meta.schema.yaml の x-used-by: ok"
else
  echo "最新の design-schemas のタグ $LATEST の schemas/meta.schema.yaml の x-used-by: failed"
  exit 1
fi
