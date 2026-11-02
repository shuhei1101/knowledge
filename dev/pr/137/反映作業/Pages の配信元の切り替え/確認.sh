#!/bin/sh
# index.yaml の確認方法の値を読むだけで観測する
set -u

failed=0

build_type=$(gh api repos/shuhei1101/knowledge/pages --jq .build_type 2>/dev/null)
if [ "$build_type" = "workflow" ]; then
  echo "build_type（$build_type）: ok"
else
  echo "build_type（$build_type）: failed"
  failed=1
fi

site=$(curl -s -o /dev/null -w '%{http_code}' https://shuhei1101.github.io/knowledge/)
if [ "$site" = "200" ]; then
  echo "サイト（$site）: ok"
else
  echo "サイト（$site）: failed"
  failed=1
fi

yaml=$(curl -s -o /dev/null -w '%{http_code}' \
  https://shuhei1101.github.io/knowledge/docs/guide/guide-setup-install-plugin.yaml)
if [ "$yaml" = "404" ]; then
  echo "公開の文書の YAML（$yaml）: ok"
else
  echo "公開の文書の YAML（$yaml）: failed"
  failed=1
fi

exit "$failed"
