#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ "$LATEST" != "design-schemas/v2.0.0" ]; then
  echo "最新の design-schemas のタグ: failed（$LATEST）"
  exit 1
fi
if git show "$LATEST:schemas/design/common.schema.yaml" | grep -qx '  decision:'; then
  echo "最新の design-schemas のタグ $LATEST の \$defs/decision: ok"
else
  echo "最新の design-schemas のタグ $LATEST の \$defs/decision: failed"
  exit 1
fi
