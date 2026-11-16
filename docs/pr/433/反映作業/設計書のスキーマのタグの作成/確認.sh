#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
STATUS=0
if [ "$LATEST" = "design-schemas/v9.0.0" ]; then
  echo "最新の design-schemas のタグ $LATEST: ok"
else
  echo "最新の design-schemas のタグ $LATEST: failed（design-schemas/v9.0.0 ではありません）"
  STATUS=1
fi
# module.schema.yaml の refs は 10 箇所あり、全てが $defs/related を指す
COUNT=$(git show "$LATEST:schemas/design/module.schema.yaml" 2>/dev/null | grep -cE '^\s*\$ref: common\.schema\.yaml#/\$defs/related$' || true)
if [ "$COUNT" -ge 10 ]; then
  echo "$LATEST の module.schema.yaml の refs が \$defs/related を指す箇所（$COUNT 件）: ok"
else
  echo "$LATEST の module.schema.yaml の refs が \$defs/related を指す箇所（$COUNT 件）: failed"
  STATUS=1
fi
exit $STATUS
