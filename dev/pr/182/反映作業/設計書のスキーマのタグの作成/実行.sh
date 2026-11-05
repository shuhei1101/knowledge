#!/bin/sh
set -eu

TAG=design-schemas/v1.0.0

# 前提確認: master の先頭に設計書のスキーマの正本が入っているか
git fetch --quiet origin master --tags
SHA=$(git rev-parse origin/master)
if ! git cat-file -e "$SHA:schemas/design/common.schema.yaml" 2>/dev/null; then
  echo "前提確認: failed（origin/master $SHA に schemas/design/ がありません）"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
REMOTE=$(git ls-remote origin "refs/tags/$TAG^{}" | cut -f1)
if [ -n "$REMOTE" ]; then
  # 既にタグがある: 同じ commit なら何もしない、違えば止める
  if [ "$REMOTE" = "$SHA" ]; then
    echo "タグの作成: skipped"
    exit 0
  fi
  echo "タグの作成: failed（$TAG は既に $REMOTE を指しています）"
  exit 1
fi
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの作成: changed"
  exit 0
fi

# 適用
git tag -a "$TAG" -m "設計書のスキーマ $TAG" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの作成: changed"
