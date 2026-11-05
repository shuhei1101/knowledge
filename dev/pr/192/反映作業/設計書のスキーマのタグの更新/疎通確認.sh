#!/bin/sh
set -eu

# origin へ読み取りだけでつながるか
if git ls-remote --exit-code origin refs/heads/master >/dev/null 2>&1; then
  echo "origin の master: ok"
else
  echo "origin の master: failed"
  exit 1
fi
