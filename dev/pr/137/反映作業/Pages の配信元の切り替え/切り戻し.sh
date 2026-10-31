#!/bin/sh
# Pages の配信元を、切り替える前のブランチ master の /docs へ戻す
set -eu

gh api -X PUT repos/shuhei1101/knowledge/pages -f build_type=legacy \
  -f 'source[branch]=master' -f 'source[path]=/docs' >/dev/null
echo "配信元の書き戻し: changed"
