#!/bin/sh
set -eu

# この PR の変更を表すマーカー（メタスキーマが x-used-by を持つ）
has_change() {
  git show "$1:schemas/meta.schema.yaml" 2>/dev/null | grep -q '^  x-used-by:'
}

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi

# 前提確認: develop にこの PR の squash commit が入っているか
git fetch --quiet origin develop --tags
SHA=$(git log origin/develop --format=%H --grep='(#266)$' -n 1)
if [ -z "$SHA" ]; then
  echo "前提確認: failed（origin/develop に件名が (#266) で終わる commit がありません）"
  exit 1
fi
if ! has_change "$SHA"; then
  echo "前提確認: failed（$SHA の schemas/meta.schema.yaml に x-used-by がありません）"
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
# 使用先の無いキーと二重のキーを削除し、既存の設計書が検査を通らなくなるため、メジャーを上げる
VERSION=${LATEST#design-schemas/v}
MAJOR=${VERSION%%.*}
TAG="design-schemas/v$((MAJOR + 1)).0.0"
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの作成: changed"
  exit 0
fi

# 適用（切り戻しが、この実行で作ったタグだけを見分けられるよう、メッセージに PR の番号を入れる）
git tag -a "$TAG" -m "設計書のスキーマ $TAG (#266)" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの作成: changed"
