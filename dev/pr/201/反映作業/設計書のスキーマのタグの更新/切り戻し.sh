#!/bin/sh
set -eu

# この PR の実行で作ったタグ（最新のタグのうち、この PR の変更を含む最も古いもの）を削除する
git fetch --quiet origin --tags
TAG=""
for candidate in $(git tag -l 'design-schemas/v*' --sort=v:refname); do
  if git show "$candidate:schemas/design/index.schema.yaml" 2>/dev/null | grep -q 'x-hidden: true'; then
    TAG=$candidate
    break
  fi
done
if [ -z "$TAG" ]; then
  echo "タグの削除: skipped"
  exit 0
fi
git push --quiet origin ":refs/tags/$TAG"
git tag -d "$TAG" >/dev/null 2>&1 || true
echo "タグの削除: changed"
