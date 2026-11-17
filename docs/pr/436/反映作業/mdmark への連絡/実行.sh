#!/bin/sh
set -eu

TAG=design-schemas/v9.1.0
BODY=$(cat <<'EOF'
knowledge の [shuhei1101/knowledge#426](https://github.com/shuhei1101/knowledge/issues/426)（作業 PR [#436](https://github.com/shuhei1101/knowledge/pull/436)）で、`schemas/design/module.schema.yaml` の `test_files` が実行環境ごとに単体テストのファイルを持てるようになりました（`maxItems: 1` を削除）。

- タグ: `design-schemas/v9.1.0`
- 作業 PR #610 で補足へ移した 2 つ目のテストファイル（Node とブラウザの単体テスト）は、設計書のスキーマの参照をこのタグへ上げれば `test_files` へ戻せます
EOF
)

# 前提確認
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed"
  exit 1
fi
if gh api repos/shuhei1101/mdmark/issues/290/comments --paginate --jq '.[].body' | grep -q "$TAG"; then
  echo "mdmark#290 へのコメント: skipped"
  exit 0
fi
if git ls-remote --tags --refs origin "$TAG" | grep -q .; then
  echo "前提確認: ok"
elif [ "${1:-}" = "--dry-run" ]; then
  echo "前提確認: ok"
  echo "タグ $TAG: missing"
else
  echo "前提確認: failed"
  echo "タグ $TAG がありません"
  exit 1
fi

# 計画（--dry-run もここを通る）
echo "--- /dev/null"
echo "+++ shuhei1101/mdmark#290 のコメント"
printf '%s\n' "$BODY" | sed 's/^/+/'
if [ "${1:-}" = "--dry-run" ]; then
  echo "mdmark#290 へのコメント: changed"
  exit 0
fi

# 適用
if ! gh issue comment 290 -R shuhei1101/mdmark --body "$BODY" >/dev/null; then
  echo "mdmark#290 へのコメント: failed"
  echo "gh issue comment 290 -R shuhei1101/mdmark --body ..."
  exit 1
fi
echo "mdmark#290 へのコメント: changed"
