#!/bin/sh
set -eu

# 設計書の参照の値を照合するリポジトリ（develop の worktree の docs/）
REPOS_GLOB='/home/shuhei2441/repo/*/.claude/worktrees/develop/docs'

# この PR の変更を表すマーカー（ref の examples に対応の取れた [ ] を含む値がある）
has_change() {
  git show "$1:schemas/design/common.schema.yaml" 2>/dev/null | grep -qF '"IF-6#request[operations[].fields].description"'
}

# 前提確認: 引数は無し（本番）か --dry-run だけ
if [ $# -gt 1 ] || { [ $# -eq 1 ] && [ "$1" != "--dry-run" ]; }; then
  echo "前提確認: failed（引数は無しか --dry-run だけです）"
  exit 1
fi

# 前提確認: develop にこの PR の squash commit が入っているか
git fetch --quiet origin develop --tags
SHA=$(git log origin/develop --format=%H --grep='(#491)$' -n 1)
if [ -z "$SHA" ]; then
  echo "前提確認: failed（origin/develop に件名が (#491) で終わる commit がありません）"
  exit 1
fi
if ! has_change "$SHA"; then
  echo "前提確認: failed（$SHA の ref の examples に IF-6#request[operations[].fields].description がありません）"
  exit 1
fi
LATEST=$(git tag -l 'design-schemas/v*' --sort=-v:refname | head -n 1)
if [ -z "$LATEST" ]; then
  echo "前提確認: failed（design-schemas のタグがありません）"
  exit 1
fi
echo "前提確認: ok"

# 計画（--dry-run もここを通る）
if has_change "$LATEST"; then
  echo "最新のタグ $LATEST はこの PR の変更を含みます"
  echo "タグの作成: skipped"
  exit 0
fi

# 参照する側の設計書の値のうち、最新のタグの pattern に一致し、squash commit の pattern に一致しない値を数える
OLD_SCHEMA=$(mktemp)
NEW_SCHEMA=$(mktemp)
trap 'rm -f "$OLD_SCHEMA" "$NEW_SCHEMA"' EXIT
git show "$LATEST:schemas/design/common.schema.yaml" > "$OLD_SCHEMA"
git show "$SHA:schemas/design/common.schema.yaml" > "$NEW_SCHEMA"
if ! NG=$(python3 -B - "$OLD_SCHEMA" "$NEW_SCHEMA" "$REPOS_GLOB" <<'PY'
import glob
import os
import re
import sys

import yaml


def patterns(path):
    defs = yaml.safe_load(open(path, encoding="utf-8"))["$defs"]
    return re.compile(defs["ref"]["pattern"]), re.compile(defs["related_item"]["properties"]["item"]["pattern"])


old_ref, old_item = patterns(sys.argv[1])
new_ref, new_item = patterns(sys.argv[2])
REF_HEAD = re.compile(r"^(?:[A-Z]+-\d+(?:-\d+)?)?#\S")
count = 0
ng = []


def walk(node, path):
    global count
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "item" and isinstance(value, str):
                count += 1
                if old_item.match(value) and not new_item.match(value):
                    ng.append(f"{path}: {value}")
            walk(value, path)
    elif isinstance(node, list):
        for value in node:
            walk(value, path)
    elif isinstance(node, str) and REF_HEAD.match(node):
        count += 1
        if old_ref.match(node) and not new_ref.match(node):
            ng.append(f"{path}: {node}")


for docs in sorted(glob.glob(sys.argv[3])):
    for path in glob.glob(os.path.join(docs, "**", "*.yaml"), recursive=True):
        rel = os.path.relpath(path, docs)
        if rel.startswith(("template/", "pr/")):
            continue
        try:
            walk(yaml.safe_load(open(path, encoding="utf-8")), path)
        except yaml.YAMLError:
            continue
for line in ng:
    print(f"一致しなくなる値: {line}", file=sys.stderr)
print(f"照合した値: {count} 件", file=sys.stderr)
print(len(ng))
PY
); then
  echo "参照する側の値の照合: failed"
  exit 1
fi
echo "参照する側の値の照合: ok（一致しなくなる値 $NG 件）"

VERSION=${LATEST#design-schemas/v}
MAJOR=${VERSION%%.*}
REST=${VERSION#*.}
MINOR=${REST%%.*}
if [ "$NG" -eq 0 ]; then
  # 参照する側の検査の結果を変えないため、マイナーを上げる
  TAG="design-schemas/v$MAJOR.$((MINOR + 1)).0"
else
  # 参照する側の検査の結果を変えるため、メジャーを上げる
  TAG="design-schemas/v$((MAJOR + 1)).0.0"
fi
echo "$TAG → $SHA"
if [ "${1:-}" = "--dry-run" ]; then
  echo "タグの作成: changed"
  exit 0
fi

# 適用（切り戻しが、この実行で作ったタグだけを見分けられるよう、メッセージに PR の番号を入れる）
git tag -a "$TAG" -m "設計書のスキーマ $TAG (#491)" "$SHA"
git push --quiet origin "refs/tags/$TAG"
echo "タグの作成: changed"
