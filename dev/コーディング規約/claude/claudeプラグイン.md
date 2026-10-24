# Claude プラグインルール

## プラグインの分け方

- プラグインは機能ごとに単独にする（利用者が個別にオンオフできる）
- 文書の MCP のプラグインは [MCP サーバー作成ルール](./mcp.md) の `## 登録` に従う

## テンプレートフォルダ

- プラグイン内のスキルなどで共通する出力形式や、重複している記載はテンプレート形式を用いる
  - {プラグインフォルダ}/templates/{日本語名}.md
- スキル内ではcatで展開する

```
<!-- 任意のスキルファイル -->
!`cat xxx/xxx.md`
```


## フックフォルダの定義
- フォルダ構成は以下とする
  - {CLAUDE_PLUGIN_ROOT}/hooks/hooks.json
  - {CLAUDE_PLUGIN_ROOT}/hooks/{フック名}/{任意のスクリプトやj2, mdファイル}
    - 例: hooks/pre-tool-use/xxx.py

## 定数管理ルール

- スキル・エージェントとそこから呼ぶ Bash のコマンドが使う定数を持つプラグインは、`{CLAUDE_PLUGIN_ROOT}/scripts/constants.sh` を用意する
- `constants.sh` には以下のルールを適用すること
  - `#!/usr/bin/env bash` で始める
  - 定数名にはプラグイン名をアッパースネークケースで付与する（例: `GH_KIT_LABEL_WIP`）
  - 各変数は `echo "export VAR=VALUE" >> "$CLAUDE_ENV_FILE"` で `$CLAUDE_ENV_FILE` に追記する
    - `$CLAUDE_ENV_FILE` は Claude Code が各 Bash コマンドの前に実行する
- `hooks/hooks.json` の `SessionStart` フックで `constants.sh` を自動実行する

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "_description": "{プラグイン名} 定数をセッション内に展開する",
            "type": "command",
            "command": "bash",
            "args": [
              "${CLAUDE_PLUGIN_ROOT}/scripts/constants.sh"
            ]
          }
        ]
      }
    ]
  }
}
```

- スキル・エージェントファイル内では手動 `source` を呼ばない
- フックが自分で読む設定は `constants.sh` に置かない
  - プラグインと一緒に配る値はプラグイン内のファイルに置き、フックが `${CLAUDE_PLUGIN_ROOT}` を起点に読む
  - 利用者の環境ごとに変わる値は、Claude Code の設定 `env` から環境変数で受け取る

## version を置かない規約

`.claude-plugin/marketplace.json` に載るプラグインは、`plugins[].version` と `plugin.json` の `version` のどちらにも version を置かない。

## 反映を叩くタイミング

稼働中のワークツリーへ入った `plugins/` 配下とリポジトリの直下の `.claude-plugin/` 配下の変更は、モニターが `update_plugins` と同じ更新を済ませてから再起動するので、手では叩かない。
自動で効かないとき（`local` で作業ツリーを修正したとき 等）は、設定 `rule_inject.source` によらず、変更の commit を載せた後に MCP ツール `update_plugins` を実行して認証領域へ反映する。
どちらの出所でも実体は認証領域の cache（`{認証領域}/plugins/cache/{マーケットプレース名}/{名前}/{version}`）の複製で、修正した作業ツリーがそのまま読まれることはない。
`update_plugins` は Claude 種別のアカウントの認証領域ごとに `claude plugin marketplace update` → `claude plugin update` の順で実行する。
