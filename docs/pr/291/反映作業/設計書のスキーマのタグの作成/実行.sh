#!/bin/sh
set -eu

# この PR の変更を表すマーカー（設計書の共通の型に文書の公開範囲がある）
has_change() {
  git show "$1:schemas/design/common.schema.yaml" 2>/dev/null | grep -q '^  doc_visibility:$'
}

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi

# 前提確認: develop にこの PR の squash commit が入っているか
git fetch --quiet origin develop --tags
SHA=$(git log origin/develop --format=%H --grep='(#291)$' -n 1)
if [ -z "$SHA" ]; then
  echo "前提確認: failed（origin/develop に件名が (#291) で終わる commit がありません）"
  exit 1
fi
if ! has_change "$SHA"; then
  echo "前提確認: failed（$SHA の schemas/design/common.schema.yaml に doc_visibility がありません）"
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
# 部品設計の最上位の visibility の値を変え、既存の設計書が検査を通らなくなりうるため、メジャーを上げる
VERSION=${LATEST#design-schemas/v}
MAJOR=${VERSION%%.*}
TAG="design-schemas/v$((MAJOR + 1)).0.0"
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの作成: changed"
  exit 0
fi

# 適用（切り戻しが、この実行で作ったタグだけを見分けられるよう、メッセージに PR の番号を入れる）
git tag -a "$TAG" -m "設計書のスキーマ $TAG (#291)" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの作成: changed"
