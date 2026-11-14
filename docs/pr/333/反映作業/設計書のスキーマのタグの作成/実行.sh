#!/bin/sh
set -eu

# この PR の変更を表すマーカー（インターフェース定義・モジュール構成のスキーマが $defs/mermaid を参照せず、map の型を参照する）
has_change() {
  for SCHEMA in schemas/design/interface.schema.yaml schemas/design/module.schema.yaml; do
    BODY=$(git show "$1:$SCHEMA" 2>/dev/null) || return 1
    echo "$BODY" | grep -qF 'common.schema.yaml#/$defs/map' || return 1
    if echo "$BODY" | grep -qF 'common.schema.yaml#/$defs/mermaid'; then
      return 1
    fi
  done
}

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi

# 前提確認: develop にこの PR の squash commit が入っているか
git fetch --quiet origin develop --tags
SHA=$(git log origin/develop --format=%H --grep='(#333)$' -n 1)
if [ -z "$SHA" ]; then
  echo "前提確認: failed（origin/develop に件名が (#333) で終わる commit がありません）"
  exit 1
fi
if ! has_change "$SHA"; then
  echo "前提確認: failed（$SHA の schemas/design/interface.schema.yaml・module.schema.yaml が \$defs/map を参照していないか、\$defs/mermaid を参照しています）"
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
# インターフェース定義の flow とモジュール構成の diagram の記載方法が変わり、既存の設計書が新しい記載方法と合わなくなるため、メジャーを上げる
VERSION=${LATEST#design-schemas/v}
MAJOR=${VERSION%%.*}
TAG="design-schemas/v$((MAJOR + 1)).0.0"
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの作成: changed"
  exit 0
fi

# 適用（切り戻しが、この実行で作ったタグだけを見分けられるよう、メッセージに PR の番号を入れる）
git tag -a "$TAG" -m "設計書のスキーマ $TAG (#333)" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの作成: changed"
