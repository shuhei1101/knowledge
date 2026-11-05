#!/bin/sh
set -eu

# この作業が作ったタグだけを削除する。#182 の反映作業が作る v1.0.0 は削除しない
git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ] || [ "$LATEST" = "design-schemas/v1.0.0" ]; then
  echo "タグの削除: skipped"
  exit 0
fi
git push --quiet origin ":refs/tags/$LATEST"
git tag -d "$LATEST" >/dev/null 2>&1 || true
echo "タグの削除: changed"
