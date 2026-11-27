#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/test_procedure.schema.yaml" | grep -qF -- '`画面の起動` のセクションを記載する。'; then
  echo "最新のタグ $LATEST の notes の 画面の起動 の決まり: ok"
else
  echo "最新のタグ $LATEST の notes の 画面の起動 の決まり: failed"
  exit 1
fi
