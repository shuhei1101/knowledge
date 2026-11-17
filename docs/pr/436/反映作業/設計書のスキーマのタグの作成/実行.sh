#!/bin/sh
set -eu

TAG=design-schemas/v9.1.0
PREV=design-schemas/v9.0.0
MESSAGE="設計書のスキーマ design-schemas/v9.1.0 (#436)"

# 前提確認
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed"
  exit 1
fi
if ! git fetch -q origin develop; then
  echo "前提確認: failed"
  echo "git fetch -q origin develop"
  exit 1
fi
if git ls-remote --tags --refs origin "$TAG" | grep -q .; then
  echo "タグの作成: skipped"
  exit 0
fi
LATEST=$(git ls-remote --tags --refs origin 'design-schemas/*' | sed 's#.*refs/tags/##' | sort -V | tail -n 1)
if [ "$LATEST" != "$PREV" ]; then
  echo "前提確認: failed"
  echo "最新のタグが $PREV ではありません: $LATEST"
  exit 1
fi
SQUASH=$(git log origin/develop --format=%H --grep='(#436)$' -n 1)
if [ -z "$SQUASH" ]; then
  if [ "${1:-}" = "--dry-run" ]; then
    echo "前提確認: ok"
    echo "develop の (#436) の squash commit: missing"
    echo "作成するタグ: $TAG（メッセージ: $MESSAGE）"
    echo "タグの作成: changed"
    exit 0
  fi
  echo "前提確認: failed"
  echo "develop に (#436) の squash commit がありません"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
echo "作成するタグ: $TAG -> $SQUASH（メッセージ: $MESSAGE）"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの作成: changed"
  exit 0
fi

# 適用
git tag -a -f "$TAG" -m "$MESSAGE" "$SQUASH"
if ! git push -q origin "refs/tags/$TAG"; then
  echo "タグの作成: failed"
  echo "git push -q origin refs/tags/$TAG"
  exit 1
fi
echo "タグの作成: changed"
