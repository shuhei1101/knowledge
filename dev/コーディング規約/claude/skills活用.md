# AgentSkills関連の知識

## 公式コンテキスト
- `https://code.claude.com/docs/en/skills.md`

## 注意事項
- 本ルールはSKILL.mdにのみ適用すること
  - CLAUDE.mdやAGENT.mdには適用されないため、注意

## スキル内の動的コンテキスト注入の書き方
- `` !`<command>` `` はスキルの内容を Claude に送信する前にシェルで実行され、出力で置き換わる
  - インライン形式は `!` が行頭か空白の直後にあるときだけ認識される（`` KEY=!`cmd` `` はリテラルのまま）
  - 複数行のコマンドは、`` ```! `` で開くフェンスコードブロックを使う
  - 出力は再展開されない。コマンドが失敗するとスキル全体の呼び出しが中止される

## スキル内の環境変数や引数の展開方法
- 展開される変数: `$ARGUMENTS`、`$ARGUMENTS[N]`、`$N`、`arguments` フロントマターで宣言した `$name`、`${CLAUDE_SESSION_ID}`、`${CLAUDE_EFFORT}`、`${CLAUDE_SKILL_DIR}`
- 数字・`ARGUMENTS`・宣言した引数名の前のリテラル `$` は、バックスラッシュでエスケープする（`\$1.00`）

## ユーザー定義環境変数を値として展開する

`$ARGUMENTS` / `${CLAUDE_SESSION_ID}` などの公式変数以外に、プラグイン側で `export` した独自環境変数（`$GH_KIT_LABEL_TYPE_FEAT` など）をスキル本文に **値として** 埋め込みたい場合のルール。

- バッククォートで挟むと Markdown のインラインコード扱いになり展開されない
  - 例: `` `$GH_KIT_LABEL_TYPE_FEAT` `` は `$GH_KIT_LABEL_TYPE_FEAT` という文字列がそのまま Claude に渡る（値を判断材料にできない）
- 値を渡したい場合は動的コンテキスト注入の `` !`echo "$VAR"` `` 形式を使う
  - 例: `` !`echo "$GH_KIT_LABEL_TYPE_FEAT"` `` はスキル読み込み時に `echo` が実行され、値（例: `type:feat`）が本文に埋め込まれる
