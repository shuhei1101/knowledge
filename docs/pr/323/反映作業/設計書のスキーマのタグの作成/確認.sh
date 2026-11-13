#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/test_procedure.schema.yaml" 2>/dev/null | grep -qF 'Git フックと CI では動かさない。'; then
  echo "最新の design-schemas のタグ $LATEST の test_procedure.schema.yaml の x-rules: ok"
else
  echo "最新の design-schemas のタグ $LATEST の test_procedure.schema.yaml の x-rules: failed"
  exit 1
fi
