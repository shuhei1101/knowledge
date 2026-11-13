#!/bin/sh
set -eu

# 環境 github-pages の配信を許すブランチを読めるか
if gh api repos/shuhei1101/knowledge/environments/github-pages/deployment-branch-policies > /dev/null 2>&1; then
  echo "環境 github-pages の配信を許すブランチの一覧: ok"
else
  echo "環境 github-pages の配信を許すブランチの一覧: failed"
  gh api repos/shuhei1101/knowledge/environments/github-pages/deployment-branch-policies
  exit 1
fi
