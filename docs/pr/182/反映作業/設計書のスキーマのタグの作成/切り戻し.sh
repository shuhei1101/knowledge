#!/bin/sh
set -eu

TAG=design-schemas/v1.0.0

# origin と手元のタグを削除する
if [ -z "$(git ls-remote origin "refs/tags/$TAG")" ]; then
  echo "タグの削除: skipped"
  exit 0
fi
git push --quiet origin ":refs/tags/$TAG"
git tag -d "$TAG" >/dev/null 2>&1 || true
echo "タグの削除: changed"
