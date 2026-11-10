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

# x-hidden は描画の注釈で、どの設計書の検査の結果も変えないので、パッチを上げる
VERSION=${LATEST#design-schemas/v}
MAJOR=${VERSION%%.*}
REST=${VERSION#*.}
MINOR=${REST%%.*}
PATCH=${REST#*.}
TAG="design-schemas/v$MAJOR.$MINOR.$((PATCH + 1))"
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの更新: changed"
  exit 0
fi

# 切り戻しが、この実行で作ったタグだけを見分けられるよう、メッセージに PR の番号を入れる
git tag -a "$TAG" -m "設計書のスキーマ $TAG (#201)" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの更新: changed"
