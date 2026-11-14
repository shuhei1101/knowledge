#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ "$LATEST" != "design-schemas/v8.3.0" ]; then
  echo "最新の design-schemas のタグ: failed（$LATEST）"
  exit 1
fi
echo "最新の design-schemas のタグ: ok（$LATEST → $(git rev-parse "$LATEST^{}")）"
LAYOUT=$(git show "$LATEST:schemas/design/layout.schema.yaml")
STATUS=0
for KEY in source tracked; do
  if printf '%s\n' "$LAYOUT" | grep -qE "^ +$KEY:\$"; then
    echo "$LATEST の layout.schema.yaml の generated_from.$KEY: ok"
  else
    echo "$LATEST の layout.schema.yaml の generated_from.$KEY: failed"
    STATUS=1
  fi
done
exit $STATUS
