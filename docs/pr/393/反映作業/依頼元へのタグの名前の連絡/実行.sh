#!/bin/sh
set -eu

TAG=design-schemas/v8.3.0

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi
# 前提確認: タグが origin にあるか
SHA=$(git ls-remote --tags origin "refs/tags/$TAG^{}" | cut -f1)
if [ -z "$SHA" ]; then
  echo "前提確認: failed（origin に $TAG がありません）"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
if gh issue view 107 --repo shuhei1101/alias-inject --json comments -q '.comments[].body' | grep -qF "$TAG"; then
  echo "コメントの投稿: skipped（$TAG を記載したコメントがあります）"
  exit 0
fi
BODY="> from: @planner

shuhei1101/knowledge#392 の \`$TAG\` を作成しました（[$SHA](https://github.com/shuhei1101/knowledge/commit/$SHA)、作業 PR shuhei1101/knowledge#393）。\`schemas/design/layout.schema.yaml\` の \`entries[].generated_from\` が \`source\`・\`tracked\` を持ちます。"
printf '%s\n' "$BODY"
if [ "${1:-}" = "--dry-run" ]; then
  echo "コメントの投稿: changed"
  exit 0
fi

# 適用
gh issue comment 107 --repo shuhei1101/alias-inject --body "$BODY" > /dev/null
echo "コメントの投稿: changed"
