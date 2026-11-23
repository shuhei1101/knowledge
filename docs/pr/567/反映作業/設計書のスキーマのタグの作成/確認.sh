#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
F=$(git show "$LATEST:schemas/design/agent_flow.schema.yaml")
for K in gates proposals unit; do
  if printf '%s\n' "$F" | grep -q "^      $K:"; then
    echo "最新のタグ $LATEST の工程の $K: ok"
  else
    echo "最新のタグ $LATEST の工程の $K: failed"
    exit 1
  fi
done
