#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git tag -l --format='%(contents:subject)' "$LATEST" | grep -qF '(#291)'; then
  echo "最新の design-schemas のタグ $LATEST のメッセージの (#291): ok"
else
  echo "最新の design-schemas のタグ $LATEST のメッセージの (#291): failed"
  exit 1
fi
if git show "$LATEST:schemas/design/common.schema.yaml" | grep -q '^  doc_visibility:$'; then
  echo "最新の design-schemas のタグ $LATEST の common.schema.yaml の doc_visibility: ok"
else
  echo "最新の design-schemas のタグ $LATEST の common.schema.yaml の doc_visibility: failed"
  exit 1
fi
