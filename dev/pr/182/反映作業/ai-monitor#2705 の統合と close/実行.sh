#!/bin/sh
set -eu

REPO=shuhei1101/ai-monitor
ISSUE=2705
BODY='設計書のスキーマの正本を knowledge に置く決定（shuhei1101/knowledge#182）で、正本を ai-monitor に置いて knowledge へ Markdown を書き出すこの Issue とは向きが逆になりました。人が読むテンプレートの生成は shuhei1101/knowledge#163 へ統合したため、この Issue は閉じます。'

# 前提確認: develop に設計書のスキーマの正本が入っているか
git fetch --quiet origin develop
SHA=$(git rev-parse origin/develop)
if ! git cat-file -e "$SHA:schemas/design/common.schema.yaml" 2>/dev/null; then
  echo "前提確認: failed（origin/develop $SHA に schemas/design/ がありません）"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
STATE=$(gh issue view "$ISSUE" -R "$REPO" --json state -q .state)
if [ "$STATE" = "CLOSED" ]; then
  echo "統合のコメントと close: skipped"
  exit 0
fi
echo "$REPO#$ISSUE（$STATE）へコメントして not planned で close する"
echo "$BODY"
if [ "${1:-}" = "--dry-run" ]; then
  echo "統合のコメントと close: changed"
  exit 0
fi

# 適用
gh issue close "$ISSUE" -R "$REPO" --reason "not planned" --comment "$BODY" >/dev/null
echo "統合のコメントと close: changed"
