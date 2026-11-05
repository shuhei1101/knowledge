#!/bin/sh
set -eu

TAG=design-schemas/v1.0.0

# タグが指す commit が master に含まれ、設計書のスキーマの正本を持つか
git fetch --quiet origin master --tags
REMOTE=$(git ls-remote origin "refs/tags/$TAG^{}" | cut -f1)
echo "$TAG: ${REMOTE:-なし}"
if [ -z "$REMOTE" ]; then
  echo "タグ: failed"
  exit 1
fi
if git merge-base --is-ancestor "$REMOTE" origin/master && git cat-file -e "$REMOTE:schemas/design/common.schema.yaml" 2>/dev/null; then
  echo "タグ: ok"
else
  echo "タグ: failed"
  exit 1
fi
