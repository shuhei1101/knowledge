#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
FLOW=$(git show "$LATEST:schemas/design/scenario.schema.yaml" 2>/dev/null | grep -A1 '^        flow:$' | tail -n 1)
if echo "$FLOW" | grep -qF 'common.schema.yaml#/$defs/map'; then
  echo "最新の design-schemas のタグ $LATEST の scenarios[].flow の参照: ok（$FLOW）"
else
  echo "最新の design-schemas のタグ $LATEST の scenarios[].flow の参照: failed（$FLOW）"
  exit 1
fi
