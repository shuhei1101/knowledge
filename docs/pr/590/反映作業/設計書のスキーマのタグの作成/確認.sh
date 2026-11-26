#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
F=$(git show "$LATEST:schemas/design/screen.schema.yaml")
COUNT=$(printf '%s\n' "$F" | grep -E '^ *description: ' | awk -F'。' 'NF > 3' | wc -l)
if [ "$COUNT" -eq 0 ]; then
  echo "最新のタグ $LATEST の 3 文以上の description: ok（0 件）"
else
  echo "最新のタグ $LATEST の 3 文以上の description: failed（$COUNT 件）"
  exit 1
fi
