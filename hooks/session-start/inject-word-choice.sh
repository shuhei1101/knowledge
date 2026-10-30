#!/usr/bin/env bash
# SessionStart フック: 規約『文章の書き方』の語の選び方の要点を additionalContext として注入する

# 公式の hooks リファレンスが定める additionalContext の文字数の上限
readonly MAX_CONTEXT_CHARS=10000
readonly RULE_FILE="${CLAUDE_PLUGIN_ROOT:-}/docs/rule/convention-writing-style.yaml"
readonly PRINCIPLE_ITEM_ID="word-choice-principle-02"
readonly MAPPING_ITEM_ID="word-choice-table-02"

# 規約の YAML から項目の本文の表のデータ行を取り出し、セルをタブ区切りで出す
extract_table_rows() {
  awk -v target="$2" '
    /^  - id: / { in_item = ($3 == target); rows = 0; next }
    in_item && /^ *\|/ {
      rows++
      # ヘッダ行と区切り行は飛ばす
      if (rows <= 2) next
      n = split($0, cell, "|")
      line = ""
      for (i = 2; i < n; i++) {
        gsub(/^ +| +$/, "", cell[i])
        line = line (i > 2 ? "\t" : "") cell[i]
      }
      print line
    }
  ' "$1"
}

# UTF-8 の文字数を数える（継続バイトを除いたバイト数）
count_chars() {
  printf '%s' "$1" | LC_ALL=C tr -d '\200-\277' | wc -c
}

# 複数行の文字列を JSON の文字列の中身（改行は \n）にする
json_escape() {
  printf '%s' "$1" | tr '\t' ' ' | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' \
    | awk 'NR > 1 { printf "%s", "\\n" } { printf "%s", $0 }'
}

main() {
  local input session_source principles mappings context chars

  input=$(cat)
  session_source=$(printf '%s' "$input" \
    | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
  case "$session_source" in
    startup | clear | compact) ;;
    *) return 0 ;;
  esac

  # 規約のファイルが読めないときは何も注入せず、セッションの開始を止めない
  [ -r "$RULE_FILE" ] || return 0

  principles=$(extract_table_rows "$RULE_FILE" "$PRINCIPLE_ITEM_ID" \
    | awk -F '\t' '{ printf "- %s（%s → %s）\n", $1, $3, $4 }')
  mappings=$(extract_table_rows "$RULE_FILE" "$MAPPING_ITEM_ID" \
    | awk -F '\t' '{ printf "- %s → %s\n", $1, $2 }')
  if [ -z "$principles" ] || [ -z "$mappings" ]; then
    echo "inject-word-choice: ${RULE_FILE} から原則表または対応表の行を取り出せなかった" >&2
    return 1
  fi

  context="語の選び方（規約『文章の書き方』の「語の選び方」）。チャットの返答・コードのコメント・ドキュメントの文章で従う。
原則（悪い例 → 良い例）:
${principles}
ドキュメントの語の対応（避ける語 → 使う語）:
${mappings}
詳しくは規約『文章の書き方』（${RULE_FILE}）を読む。"

  chars=$(( $(count_chars "$context") ))
  if [ "$chars" -gt "$MAX_CONTEXT_CHARS" ]; then
    echo "inject-word-choice: 注入する文が ${chars} 文字で、上限の ${MAX_CONTEXT_CHARS} 文字を超えた" >&2
    return 1
  fi

  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' \
    "$(json_escape "$context")"
}

main
