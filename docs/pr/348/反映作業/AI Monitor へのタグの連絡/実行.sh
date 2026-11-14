#!/bin/sh
set -eu

REPO=shuhei1101/ai-monitor
NUMBER=3430
LABEL=確認:planner
MARKER='(shuhei1101/knowledge#348)'

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi

# 前提確認: 反映作業『設計書のスキーマのタグの作成』が作ったタグ（メッセージに (#348)）があるか
git fetch --quiet origin --tags
TAG=""
for T in $(git tag -l 'design-schemas/v*' --sort=-v:refname); do
  if git tag -l --format='%(contents:subject)' "$T" | grep -qF '(#348)'; then
    TAG=$T
    break
  fi
done
if [ -z "$TAG" ]; then
  echo "前提確認: failed（メッセージに (#348) を持つ design-schemas のタグがありません）"
  exit 1
fi
STATE=$(gh pr view "$NUMBER" --repo "$REPO" --json state -q .state)
if [ "$STATE" != "OPEN" ]; then
  echo "前提確認: failed（$REPO#$NUMBER が open ではありません: $STATE）"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
posted_at() {
  gh api "repos/$REPO/issues/$NUMBER/comments" --paginate -q ".[] | select(.body | contains(\"$MARKER\")) | select(.body | contains(\"$TAG\")) | .created_at" | head -n 1
}
POSTED_AT=$(posted_at)
BODY=$(printf '> from: %s\n> to: @planner\n\nknowledge の設計書のスキーマのタグ `%s` を打ちました %s。\n`dev-docs.yaml` の `documents[].schema` の `ref` をこのタグへ切り替えてください。' "shuhei1101/knowledge#348" "$TAG" "$MARKER")
if [ -n "$POSTED_AT" ]; then
  echo "会話欄へのタグの名前の記載: skipped"
else
  echo "$REPO#$NUMBER の会話欄へ記載する本文:"
  echo "$BODY"
  if [ "${1:-}" = "--dry-run" ]; then
    echo "会話欄へのタグの名前の記載: changed"
    echo "$LABEL の付与: changed"
    exit 0
  fi
  gh pr comment "$NUMBER" --repo "$REPO" --body "$BODY" > /dev/null
  echo "会話欄へのタグの名前の記載: changed"
  POSTED_AT=$(posted_at)
fi
# 記載したコメント以後に付与のイベントがあれば済み。前から付いているだけのラベルは付け直して、記載の後の付与にする
LABELED_AT=$(gh api "repos/$REPO/issues/$NUMBER/events" --paginate -q ".[] | select(.event == \"labeled\" and .label.name == \"$LABEL\" and .created_at >= \"$POSTED_AT\") | .created_at" | head -n 1)
if [ -n "$LABELED_AT" ]; then
  echo "$LABEL の付与: skipped"
  exit 0
fi
if [ "${1:-}" = "--dry-run" ]; then
  echo "$LABEL の付与: changed"
  exit 0
fi
if gh pr view "$NUMBER" --repo "$REPO" --json labels -q ".labels[].name" | grep -qxF "$LABEL"; then
  gh pr edit "$NUMBER" --repo "$REPO" --remove-label "$LABEL" > /dev/null
fi
gh pr edit "$NUMBER" --repo "$REPO" --add-label "$LABEL" > /dev/null
echo "$LABEL の付与: changed"
