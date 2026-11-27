#!/bin/sh
set -eu

# この PR の変更を表すマーカー（テスト実行方法のスキーマの notes の x-rules に、画面の起動のセクションの決まりがある）
has_change() {
  F=$(git show "$1:schemas/design/test_procedure.schema.yaml" 2>/dev/null) || return 1
  printf '%s\n' "$F" | grep -qF -- '実装した画面を作業ブランチの worktree から開く手順を持つプロジェクトは、`画面の起動` のセクションを記載する。' || return 1
  return 0
}

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi

# 前提確認: develop にこの PR の squash commit が入っているか
git fetch --quiet origin develop --tags
SHA=$(git log origin/develop --format=%H --grep='(#593)$' -n 1)
if [ -z "$SHA" ]; then
  echo "前提確認: failed（origin/develop に件名が (#593) で終わる commit がありません）"
  exit 1
fi
if ! has_change "$SHA"; then
  echo "前提確認: failed（$SHA の テスト実行方法のスキーマの notes に 画面の起動 の決まりがありません）"
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
# x-rules と examples の追加で既存の設計書の検査の結果を変えないため、パッチを上げる
VERSION=${LATEST#design-schemas/v}
MAJOR=${VERSION%%.*}
REST=${VERSION#*.}
MINOR=${REST%%.*}
PATCH=${REST#*.}
TAG="design-schemas/v$MAJOR.$MINOR.$((PATCH + 1))"
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの作成: changed"
  exit 0
fi

# 適用（切り戻しが、この実行で作ったタグだけを見分けられるよう、メッセージに PR の番号を入れる）
git tag -a "$TAG" -m "設計書のスキーマ $TAG (#593)" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの作成: changed"
