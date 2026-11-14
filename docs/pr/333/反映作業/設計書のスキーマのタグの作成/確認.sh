#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
STATUS=0
for SCHEMA in schemas/design/interface.schema.yaml schemas/design/module.schema.yaml; do
  COUNT=$(git show "$LATEST:$SCHEMA" 2>/dev/null | grep -cF 'common.schema.yaml#/$defs/mermaid' || true)
  if [ "$COUNT" -eq 0 ]; then
    echo "最新の design-schemas のタグ $LATEST の $SCHEMA の \$defs/mermaid の参照: ok（0 件）"
  else
    echo "最新の design-schemas のタグ $LATEST の $SCHEMA の \$defs/mermaid の参照: failed（$COUNT 件）"
    STATUS=1
  fi
done
exit $STATUS
