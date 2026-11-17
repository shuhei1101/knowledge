#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
PATTERN=$(git show "$LATEST:schemas/design/module.schema.yaml" | python3 -B -c 'import sys, yaml; print(yaml.safe_load(sys.stdin)["properties"]["test_files"]["items"]["pattern"])')
if python3 -B -c 'import re, sys; p = re.compile(sys.argv[1]); sys.exit(0 if all(p.search(v) for v in ["tests/unit/a.test.ts", "frontend/src/a.test.ts", "frontend/src/a.test.tsx"]) else 1)' "$PATTERN"; then
  echo "最新のタグ $LATEST の test_files の pattern: ok（$PATTERN）"
else
  echo "最新のタグ $LATEST の test_files の pattern: failed（$PATTERN）"
  exit 1
fi
