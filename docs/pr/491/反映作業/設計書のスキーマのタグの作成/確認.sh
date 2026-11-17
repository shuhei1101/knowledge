#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
if git show "$LATEST:schemas/design/common.schema.yaml" 2>/dev/null | grep -qF '"IF-6#request[operations[].fields].description"'; then
  echo "最新のタグ $LATEST の ref の examples: ok（IF-6#request[operations[].fields].description があります）"
else
  echo "最新のタグ $LATEST の ref の examples: failed（IF-6#request[operations[].fields].description がありません）"
  exit 1
fi
