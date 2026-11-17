#!/bin/sh
set -eu

TAG=design-schemas/v9.1.0

git fetch -q origin "refs/tags/$TAG:refs/tags/$TAG"
if ! git for-each-ref "refs/tags/$TAG" --format='%(contents:subject)' | grep -q '(#436)$'; then
  echo "タグのメッセージ: failed"
  git for-each-ref "refs/tags/$TAG" --format='%(contents:subject)'
  exit 1
fi
git push -q origin ":refs/tags/$TAG"
git tag -d "$TAG" >/dev/null
echo "タグの削除: changed"
