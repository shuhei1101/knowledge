#!/bin/sh
set -eu

TAG=design-schemas/v9.1.0

LATEST=$(git ls-remote --tags --refs origin 'design-schemas/*' | sed 's#.*refs/tags/##' | sort -V | tail -n 1)
if [ "$LATEST" = "$TAG" ]; then
  echo "最新のタグ: ok"
else
  echo "最新のタグ: failed"
  echo "最新のタグ: $LATEST"
  exit 1
fi

git fetch -q origin "refs/tags/$TAG:refs/tags/$TAG"
if git show "$TAG:schemas/design/module.schema.yaml" | sed -n '/^  test_files:/,/^  [a-z_]*:$/p' | grep -q 'maxItems: 1'; then
  echo "test_files の maxItems: failed"
  git show "$TAG:schemas/design/module.schema.yaml" | sed -n '/^  test_files:/,/^  [a-z_]*:$/p'
  exit 1
fi
echo "test_files の maxItems: ok"
