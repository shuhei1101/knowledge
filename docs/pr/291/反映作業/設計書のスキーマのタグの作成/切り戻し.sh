#!/bin/sh
set -eu

git fetch --quiet origin --tags
FOUND=0
for TAG in $(git tag -l 'design-schemas/v*'); do
  if git tag -l --format='%(contents:subject)' "$TAG" | grep -qF '(#291)'; then
    git push --quiet origin ":refs/tags/$TAG"
    git tag -d "$TAG" > /dev/null
    echo "タグ $TAG の削除: changed"
    FOUND=1
  fi
done
if [ "$FOUND" -eq 0 ]; then
  echo "タグの削除: skipped（メッセージに (#291) を持つタグがありません）"
fi
