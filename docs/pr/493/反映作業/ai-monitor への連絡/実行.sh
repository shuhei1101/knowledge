#!/bin/sh
set -eu

# 前提確認
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed"
  exit 1
fi
git fetch --quiet origin --tags
TAG=""
for T in $(git tag -l 'design-schemas/v*'); do
  if git tag -l --format='%(contents:subject)' "$T" | grep -qF '(#493)'; then
    TAG=$T
  fi
done
if [ -z "$TAG" ]; then
  if [ "${1:-}" = "--dry-run" ]; then
    echo "前提確認: ok"
    echo "メッセージに (#493) を持つタグ: missing"
    TAG='design-schemas/v{作成したタグ}'
  else
    echo "前提確認: failed"
    echo "メッセージに (#493) を持つ design-schemas のタグがありません"
    exit 1
  fi
else
  if gh api repos/shuhei1101/ai-monitor/issues/3607/comments --paginate --jq '.[].body' | grep -qF "$TAG"; then
    echo "ai-monitor#3607 へのコメント: skipped"
    exit 0
  fi
  echo "前提確認: ok"
fi

BODY=$(cat <<BODY_EOF
knowledge の [shuhei1101/knowledge#492](https://github.com/shuhei1101/knowledge/issues/492)（作業 PR [#493](https://github.com/shuhei1101/knowledge/pull/493)）で、\`schemas/design/module.schema.yaml\` の \`test_files\` に、規約『フォルダ構成』のとおり対象の横に配置した単体テストのファイル（\`*.test.ts\`・\`*.test.tsx\`）を記載できるようになりました（\`pattern\` を \`^(?:tests/.+|.+\.test\.tsx?)$\` に変更）。

- タグ: \`$TAG\`
- 設計書のスキーマの参照をこのタグへ上げれば、記載せずに進めた画面のフロントエンドのモジュール構成の \`test_files\` に \`frontend/src/...test.ts(x)\` を記載できます
BODY_EOF
)

# 計画（--dry-run もここを通る）
echo "--- /dev/null"
echo "+++ shuhei1101/ai-monitor#3607 のコメント"
printf '%s\n' "$BODY" | sed 's/^/+/'
if [ "${1:-}" = "--dry-run" ]; then
  echo "ai-monitor#3607 へのコメント: changed"
  exit 0
fi

# 適用
if ! gh pr comment 3607 -R shuhei1101/ai-monitor --body "$BODY" >/dev/null; then
  echo "ai-monitor#3607 へのコメント: failed"
  echo "gh pr comment 3607 -R shuhei1101/ai-monitor --body ..."
  exit 1
fi
echo "ai-monitor#3607 へのコメント: changed"
