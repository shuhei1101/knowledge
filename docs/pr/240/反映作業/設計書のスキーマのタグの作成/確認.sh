#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/common.schema.yaml" | grep -qF 'contentMediaType: text/markdown'; then
  echo "最新の design-schemas のタグ $LATEST の \$defs/markdown の contentMediaType: ok"
else
  echo "最新の design-schemas のタグ $LATEST の \$defs/markdown の contentMediaType: failed"
  exit 1
fi
