#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
STATUS=0
if git show "$LATEST:schemas/design/architecture.schema.yaml" 2>/dev/null | grep -qF 'common.schema.yaml#/$defs/aliases'; then
  echo "最新の design-schemas のタグ $LATEST の architecture.schema.yaml の \$defs/aliases の参照: ok"
else
  echo "最新の design-schemas のタグ $LATEST の architecture.schema.yaml の \$defs/aliases の参照: failed"
  STATUS=1
fi
if git show "$LATEST:schemas/knowledge-files.schema.yaml" 2>/dev/null | grep -qF 'inject_when:'; then
  echo "最新の design-schemas のタグ $LATEST の knowledge-files.schema.yaml の inject_when: ok"
else
  echo "最新の design-schemas のタグ $LATEST の knowledge-files.schema.yaml の inject_when: failed"
  STATUS=1
fi
exit $STATUS
