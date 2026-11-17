#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
FAILED=0
# スキーマ・一致すべき値の順に、test_file の pattern を確かめる
for ENTRY in \
  "component|tests/integration/a/test_a.py|frontend/src/features/a/shared/components/a.test.tsx" \
  "screen|tests/integration/a/test_a.py|frontend/src/features/a/b/b-screen.test.tsx" \
  "scenario|tests/e2e/単一ユースケース/test_a.py|frontend/tests/e2e/単一ユースケース/a.spec.ts"; do
  NAME=${ENTRY%%|*}
  VALUES=${ENTRY#*|}
  PATTERN=$(git show "$LATEST:schemas/design/$NAME.schema.yaml" | python3 -B -c 'import sys, yaml; print(yaml.safe_load(sys.stdin)["properties"]["test_file"]["pattern"])')
  if python3 -B -c 'import re, sys; p = re.compile(sys.argv[1]); sys.exit(0 if all(p.search(v) for v in sys.argv[2].split("|")) else 1)' "$PATTERN" "$VALUES"; then
    echo "最新のタグ $LATEST の $NAME の test_file の pattern: ok（$PATTERN）"
  else
    echo "最新のタグ $LATEST の $NAME の test_file の pattern: failed（$PATTERN）"
    FAILED=1
  fi
done
exit "$FAILED"
