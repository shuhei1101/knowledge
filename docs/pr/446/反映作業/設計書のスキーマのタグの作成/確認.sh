#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git cat-file -e "$LATEST:schemas/design/glossary.schema.yaml" 2>/dev/null; then
  echo "最新のタグ $LATEST の用語集のスキーマ: ok"
else
  echo "最新のタグ $LATEST の用語集のスキーマ: failed"
  exit 1
fi
if git show "$LATEST:schemas/design/common.schema.yaml" 2>/dev/null | grep -qF '../interface/IF-72-3.py.yaml#flows'; then
  echo "最新のタグ $LATEST の clicks[].href の例の相対パス: failed（残っています）"
  exit 1
fi
echo "最新のタグ $LATEST の clicks[].href の例の相対パス: ok（ありません）"
