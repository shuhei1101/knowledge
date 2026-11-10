#!/bin/sh
# Pages の配信元を GitHub Actions へ切り替え、公開文書の配信のワークフローを master で 1 回動かす
set -u

REPO=shuhei1101/knowledge

# 前提確認
build_type=$(gh api "repos/$REPO/pages" --jq .build_type 2>/dev/null) || {
  echo "前提確認: failed（Pages の設定を読めません）"
  exit 1
}
if ! gh api "repos/$REPO/contents/.github/workflows/pages.yml?ref=master" --jq .path >/dev/null 2>&1; then
  echo "前提確認: failed（master に .github/workflows/pages.yml がありません）"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
master_sha=$(gh api "repos/$REPO/commits/master" --jq .sha)
deployed=$(gh run list -R "$REPO" --workflow pages.yml --branch master --status success \
  --json headSha --jq "[.[] | select(.headSha == \"$master_sha\")] | length")
if [ "$build_type" = "workflow" ]; then
  switch=skipped
else
  switch=changed
  echo "--- repos/$REPO/pages"
  echo "+++ repos/$REPO/pages"
  echo "-build_type: $build_type"
  echo "+build_type: workflow"
fi
if [ "$switch" = "skipped" ] && [ "$deployed" -gt 0 ]; then
  run=skipped
else
  run=changed
  echo "master（$master_sha）で pages.yml を workflow_dispatch で起動する"
fi
if [ "${1:-}" = "--dry-run" ]; then
  echo "配信元の切り替え: $switch"
  echo "ワークフローの実行: $run"
  exit 0
fi

# 適用
if [ "$switch" = "changed" ]; then
  if ! gh api -X PUT "repos/$REPO/pages" -f build_type=workflow >/dev/null; then
    echo "配信元の切り替え: failed"
    exit 1
  fi
fi
echo "配信元の切り替え: $switch"

if [ "$run" = "skipped" ]; then
  echo "ワークフローの実行: skipped"
  exit 0
fi
started=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if ! gh workflow run pages.yml -R "$REPO" --ref master; then
  echo "ワークフローの実行: failed（起動できません）"
  exit 1
fi
# 起動した実行が一覧に出るまで待つ（5 秒ごとに 24 回まで）
run_id=""
tries=0
until [ -n "$run_id" ] || [ "$tries" -ge 24 ]; do
  sleep 5
  tries=$((tries + 1))
  run_id=$(gh run list -R "$REPO" --workflow pages.yml --event workflow_dispatch --limit 5 \
    --json databaseId,createdAt --jq "[.[] | select(.createdAt >= \"$started\")][0].databaseId // empty")
done
if [ -z "$run_id" ]; then
  echo "ワークフローの実行: failed（起動した実行が見つかりません）"
  exit 1
fi
if ! gh run watch "$run_id" -R "$REPO" --exit-status >/dev/null; then
  echo "ワークフローの実行: failed（https://github.com/$REPO/actions/runs/$run_id）"
  exit 1
fi
echo "ワークフローの実行: changed（https://github.com/$REPO/actions/runs/$run_id）"
