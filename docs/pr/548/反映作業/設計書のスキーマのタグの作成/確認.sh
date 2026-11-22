#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/data.schema.yaml" 2>/dev/null | grep -qF "pattern: '^データ: .+\$'"; then
  echo "最新のタグ $LATEST のデータのスキーマの前置きの pattern: failed（残っています）"
  exit 1
fi
echo "最新のタグ $LATEST のデータのスキーマの前置きの pattern: ok（ありません）"
