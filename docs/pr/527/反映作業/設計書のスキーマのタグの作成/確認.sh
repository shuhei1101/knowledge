#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
# 用語集のスキーマの用語が details を持つかを確かめる
if git show "$LATEST:schemas/terms.schema.yaml" | python3 -B -c 'import sys, yaml; d = yaml.safe_load(sys.stdin); sys.exit(0 if "details" in d["$defs"]["term"]["properties"] else 1)'; then
  echo "最新のタグ $LATEST の用語集の用語の details: ok"
else
  echo "最新のタグ $LATEST の用語集の用語の details: failed"
  exit 1
fi
