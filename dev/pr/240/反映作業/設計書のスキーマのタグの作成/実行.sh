#!/bin/sh
set -eu

# この PR の変更を表す、設計書の共通の型の中の印（$defs/markdown の contentMediaType）
has_change() {
  git show "$1:schemas/design/common.schema.yaml" 2>/dev/null | grep -qF 'contentMediaType: text/markdown'
}

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi

# 前提確認: develop にこの PR の squash commit が入っているか
git fetch --quiet origin develop --tags
SHA=$(git log origin/develop --format=%H --grep='(#240)$' -n 1)
if [ -z "$SHA" ]; then
  echo "前提確認: failed（origin/develop に件名が (#240) で終わる commit がありません）"
  exit 1
fi
if ! has_change "$SHA"; then
  echo "前提確認: failed（$SHA の schemas/design/common.schema.yaml に contentMediaType: text/markdown がありません）"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -n "$LATEST" ] && has_change "$LATEST"; then
  echo "最新のタグ $LATEST はこの PR の変更を含みます"
  echo "タグの作成: skipped"
  exit 0
fi
if [ -z "$LATEST" ]; then
  TAG="design-schemas/v1.0.0"
else
  # 本文の点検が増える変更のため、マイナーを上げる
  VERSION=${LATEST#design-schemas/v}
  MAJOR=${VERSION%%.*}
  REST=${VERSION#*.}
  MINOR=${REST%%.*}
  TAG="design-schemas/v$MAJOR.$((MINOR + 1)).0"
fi
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの作成: changed"
  exit 0
fi

# 適用（切り戻しが、この実行で作ったタグだけを見分けられるよう、メッセージに PR の番号を入れる）
git tag -a "$TAG" -m "設計書のスキーマ $TAG (#240)" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの作成: changed"
