#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/common.schema.yaml" 2>/dev/null | grep -qF 'id:IF-72-3#flows[正常系]'; then
  echo "最新のタグ $LATEST の clicks[].href の id: のリンクの例: ok"
else
  echo "最新のタグ $LATEST の clicks[].href の id: のリンクの例: failed"
  exit 1
fi
