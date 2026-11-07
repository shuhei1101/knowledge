#!/bin/sh
set -eu

# 実行.sh が作ったタグ（メッセージに (#223) を持つ design-schemas/v* のタグ）だけを削除する
git fetch --quiet origin --tags
TAG=""
for candidate in $(git tag -l 'design-schemas/v*'); do
  if git tag -l --format='%(contents:subject)' "$candidate" | grep -qF '(#223)'; then
    TAG=$candidate
  fi
done
if [ -z "$TAG" ]; then
  echo "タグの削除: skipped"
  exit 0
fi
git push --quiet origin ":refs/tags/$TAG"
git tag -d "$TAG" >/dev/null 2>&1 || true
echo "タグの削除: changed"
