#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git cat-file -e "$LATEST:schemas/design/data.schema.yaml" 2>/dev/null; then
  echo "最新の design-schemas のタグ $LATEST の schemas/design/data.schema.yaml: ok"
else
  echo "最新の design-schemas のタグ $LATEST の schemas/design/data.schema.yaml: failed"
  exit 1
fi
if git show "$LATEST:schemas/design/er.schema.yaml" | grep -q '^      - source$'; then
  echo "最新の design-schemas のタグ $LATEST の er.schema.yaml の tables[].source の必須: ok"
else
  echo "最新の design-schemas のタグ $LATEST の er.schema.yaml の tables[].source の必須: failed"
  exit 1
fi
