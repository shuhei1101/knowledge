#!/bin/sh
# Pages の設定・ワークフロー・サイトに読み取りだけでつながるかを確かめる
set -u

failed=0

if gh api repos/shuhei1101/knowledge/pages --jq .build_type >/dev/null 2>&1; then
  echo "Pages の設定: ok"
else
  echo "Pages の設定: failed"
  failed=1
fi

if gh api repos/shuhei1101/knowledge/actions/workflows/pages.yml --jq .state >/dev/null 2>&1; then
  echo "公開文書の配信のワークフロー: ok"
else
  echo "公開文書の配信のワークフロー: failed"
  failed=1
fi

if curl -s -o /dev/null https://shuhei1101.github.io/knowledge/; then
  echo "Pages のサイト: ok"
else
  echo "Pages のサイト: failed"
  failed=1
fi

exit "$failed"
