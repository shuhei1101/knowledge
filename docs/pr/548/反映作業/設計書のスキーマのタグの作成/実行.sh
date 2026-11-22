#!/bin/sh
set -eu

# この PR の変更を表すマーカー（データのスキーマの title に前置きを求める pattern が無く、前置きを付けない決まりがある）
has_change() {
  SCHEMA=$(git show "$1:schemas/design/data.schema.yaml" 2>/dev/null) || return 1
  printf '%s\n' "$SCHEMA" | grep -qF "pattern: '^データ: .+\$'" && return 1
  printf '%s\n' "$SCHEMA" | grep -qF '前置きに付けない' || return 1
  return 0
}

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi

# 前提確認: develop にこの PR の squash commit が入っているか
git fetch --quiet origin develop --tags
SHA=$(git log origin/develop --format=%H --grep='(#548)$' -n 1)
if [ -z "$SHA" ]; then
  echo "前提確認: failed（origin/develop に件名が (#548) で終わる commit がありません）"
  exit 1
fi
if ! has_change "$SHA"; then
  echo "前提確認: failed（$SHA のデータのスキーマに、前置きを付けない決まりが無いか、前置きを求める pattern が残っています）"
  exit 1
fi
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "前提確認: failed（design-schemas のタグがありません）"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
if has_change "$LATEST"; then
  echo "最新のタグ $LATEST はこの PR の変更を含みます"
  echo "タグの作成: skipped"
  exit 0
fi
# 説明と x-rules の変更と pattern を外す変更で、既存の設計書は検査を通ったままなので、マイナーを上げる
VERSION=${LATEST#design-schemas/v}
MAJOR=${VERSION%%.*}
REST=${VERSION#*.}
MINOR=${REST%%.*}
TAG="design-schemas/v$MAJOR.$((MINOR + 1)).0"
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの作成: changed"
  exit 0
fi

# 適用（切り戻しが、この実行で作ったタグだけを見分けられるよう、メッセージに PR の番号を入れる）
git tag -a "$TAG" -m "設計書のスキーマ $TAG (#548)" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの作成: changed"
