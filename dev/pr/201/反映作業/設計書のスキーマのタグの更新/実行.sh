#!/bin/sh
set -eu

# この PR の変更を表す、設計書のスキーマの中の印（docs_index の x-hidden）
has_change() {
  git show "$1:schemas/design/index.schema.yaml" 2>/dev/null | grep -q 'x-hidden: true'
}

# 前提確認: master の先頭にこの PR の変更が入っているか
git fetch --quiet origin master --tags
SHA=$(git rev-parse origin/master)
if ! has_change "$SHA"; then
  echo "前提確認: failed（origin/master $SHA の schemas/design/index.schema.yaml に x-hidden がありません）"
  exit 1
fi
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "前提確認: failed（design-schemas/v* のタグがありません。#182 の反映作業が先です）"
  exit 1
fi

# 最新のタグがこの PR の変更を含むなら何もしない
if has_change "$LATEST"; then
  echo "前提確認: ok"
  echo "タグの更新: skipped"
  exit 0
fi
echo "前提確認: ok"

# キーの追加だけなので、マイナーを上げてパッチを 0 にする
VERSION=${LATEST#design-schemas/v}
MAJOR=${VERSION%%.*}
REST=${VERSION#*.}
MINOR=${REST%%.*}
TAG="design-schemas/v$MAJOR.$((MINOR + 1)).0"
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの更新: changed"
  exit 0
fi

git tag -a "$TAG" -m "設計書のスキーマ $TAG" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの更新: changed"
