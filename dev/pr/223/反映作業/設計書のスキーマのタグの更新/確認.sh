#!/bin/sh
set -eu

# 最新のタグが master に含まれ、この PR の変更を持つか
git fetch --quiet origin master --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
echo "最新のタグ: ${LATEST:-なし}"
if [ -n "$LATEST" ] && git merge-base --is-ancestor "$LATEST" origin/master && git show "$LATEST:schemas/design/scenario.schema.yaml" 2>/dev/null | grep -qF '…`（規約『V字モデル』）'; then
  echo "タグ: ok"
else
  echo "タグ: failed"
  exit 1
fi
