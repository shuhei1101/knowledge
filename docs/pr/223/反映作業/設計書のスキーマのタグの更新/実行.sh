#!/bin/sh
set -eu

# この PR の変更を表す、設計書のスキーマの中の印（シナリオの test_file の規約『V字モデル』への参照）
has_change() {
  git show "$1:schemas/design/scenario.schema.yaml" 2>/dev/null | grep -qF '…`（規約『V字モデル』）'
}

# 前提確認: master の先頭にこの PR の変更が入っているか
git fetch --quiet origin master --tags
SHA=$(git rev-parse origin/master)
if ! has_change "$SHA"; then
  echo "前提確認: failed（origin/master $SHA の schemas/design/scenario.schema.yaml に規約『V字モデル』への参照がありません）"
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

# 説明と x-rules の文言の追加だけで、どの設計書の検査の結果も変えないので、パッチを上げる
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
git tag -a "$TAG" -m "設計書のスキーマ $TAG (#223)" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの更新: changed"
