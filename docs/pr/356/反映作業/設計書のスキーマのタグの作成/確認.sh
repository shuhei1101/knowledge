#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
STATUS=0
if git show "$LATEST:schemas/design/test_procedure.schema.yaml" 2>/dev/null | grep -qF 'run_runner:'; then
  echo "最新の design-schemas のタグ $LATEST の test_procedure.schema.yaml の run_runner: ok"
else
  echo "最新の design-schemas のタグ $LATEST の test_procedure.schema.yaml の run_runner: failed"
  STATUS=1
fi
if git show "$LATEST:schemas/design/interface.schema.yaml" 2>/dev/null | grep -qF 'overall_flow:'; then
  echo "最新の design-schemas のタグ $LATEST の interface.schema.yaml の overall_flow: ok"
else
  echo "最新の design-schemas のタグ $LATEST の interface.schema.yaml の overall_flow: failed"
  STATUS=1
fi
exit $STATUS
