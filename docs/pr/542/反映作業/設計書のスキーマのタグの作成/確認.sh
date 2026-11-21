#!/bin/sh
set -eu

git fetch --quiet origin --tags
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "最新の design-schemas のタグ: failed（タグがありません）"
  exit 1
fi
for F in human_escalation review_checklist; do
  if git cat-file -e "$LATEST:schemas/design/$F.schema.yaml" 2>/dev/null; then
    echo "最新のタグ $LATEST の $F のスキーマ: ok"
  else
    echo "最新のタグ $LATEST の $F のスキーマ: failed"
    exit 1
  fi
done
if git show "$LATEST:schemas/design/eval_criterion.schema.yaml" 2>/dev/null | grep -qF '設ける場合'; then
  echo "最新のタグ $LATEST の観点の語彙の表の決まり: ok"
else
  echo "最新のタグ $LATEST の観点の語彙の表の決まり: failed"
  exit 1
fi
