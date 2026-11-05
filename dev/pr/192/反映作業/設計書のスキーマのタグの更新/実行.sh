#!/bin/sh
set -eu

# 前提確認: master の先頭にこの PR の変更が入っているか
git fetch --quiet origin master --tags
SHA=$(git rev-parse origin/master)
if ! git cat-file -e "$SHA:schemas/meta.schema.yaml" 2>/dev/null; then
  echo "前提確認: failed（origin/master $SHA に schemas/meta.schema.yaml がありません）"
  exit 1
fi
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "前提確認: failed（design-schemas/v* のタグがありません。#182 の反映作業が先です）"
  exit 1
fi
echo "前提確認: ok"

# 最新のタグがこの PR の変更を含むなら何もしない
if git cat-file -e "$LATEST:schemas/meta.schema.yaml" 2>/dev/null; then
  echo "タグの更新: skipped"
  exit 0
fi

# インターフェース定義の status_codes と exceptions の併記を禁じたので、メジャーを上げる
MAJOR=$(echo "$LATEST" | sed 's|design-schemas/v\([0-9]*\)\..*|\1|')
TAG="design-schemas/v$((MAJOR + 1)).0.0"
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの更新: changed"
  exit 0
fi

git tag -a "$TAG" -m "設計書のスキーマ $TAG" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの更新: changed"
