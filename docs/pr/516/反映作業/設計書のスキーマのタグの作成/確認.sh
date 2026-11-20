#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
# データの fields[] の要素が condition を持つかを確かめる
if git show "$LATEST:schemas/design/data.schema.yaml" | python3 -B -c 'import sys, yaml; d = yaml.safe_load(sys.stdin); sys.exit(0 if "condition" in d["properties"]["fields"]["items"]["properties"] else 1)'; then
  echo "最新のタグ $LATEST のデータの fields[].condition: ok"
else
  echo "最新のタグ $LATEST のデータの fields[].condition: failed"
  exit 1
fi
