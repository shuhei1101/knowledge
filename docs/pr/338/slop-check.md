# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/scenario/SC-148-1.yaml](https://github.com/shuhei1101/knowledge/blob/fabdc4c0a0acc72ea677fb6357fd2dc79617c425/docs/scenario/SC-148-1.yaml) | エージェントが書き込んだ中身の AI slop の単語を通知される | 通知は NG と OK の表だけ。103 行の分岐の説明は project-index の `write_docs` だけ |
| ドキュメント | [docs/interface/IF-148-1.py.yaml](https://github.com/shuhei1101/knowledge/blob/fabdc4c0a0acc72ea677fb6357fd2dc79617c425/docs/interface/IF-148-1.py.yaml) | 書き込んだ中身の照合 | 出力は `additionalContext` だけ。156・181 行のテストの入力と 360・361 行の対象のツールは project-index の名前だけ |
| ドキュメント | [docs/module/MOD-148-2.py.yaml](https://github.com/shuhei1101/knowledge/blob/fabdc4c0a0acc72ea677fb6357fd2dc79617c425/docs/module/MOD-148-2.py.yaml) | slop-check / hooks / slop_check.py | 60 行の `MCP_TOOLS` のキー、95 行の `NOTICE_TAIL`、197・203 行の `is_target` のテストの条件 |
| ドキュメント | [docs/module/MOD-148-1.yaml](https://github.com/shuhei1101/knowledge/blob/fabdc4c0a0acc72ea677fb6357fd2dc79617c425/docs/module/MOD-148-1.yaml) | slop-check / hooks | フォルダの構成。変えるかはモジュール構成設計で確認する |
| 実装 | [plugins/slop-check/hooks/post-tool-use/slop_check.py](https://github.com/shuhei1101/knowledge/blob/fabdc4c0a0acc72ea677fb6357fd2dc79617c425/plugins/slop-check/hooks/post-tool-use/slop_check.py) | 書き込んだ中身の照合のフック | 36 行の `MCP_TOOLS`、100・102 行の `NOTICE_TAIL`、191 行の出力 |
| 実装 | [plugins/slop-check/hooks/hooks.json](https://github.com/shuhei1101/knowledge/blob/fabdc4c0a0acc72ea677fb6357fd2dc79617c425/plugins/slop-check/hooks/hooks.json) | フックの登録 | `_description` が「additionalContext で通知する」 |
| テスト | [tests/unit/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/fabdc4c0a0acc72ea677fb6357fd2dc79617c425/tests/unit/slop-check/test_slop_check.py) | 単体テスト | 173・190・214・233・276 行のツール名 |
| テスト | [tests/integration/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/fabdc4c0a0acc72ea677fb6357fd2dc79617c425/tests/integration/slop-check/test_slop_check.py) | 結合テスト | 144・158 行のツール名。出力は `additionalContext` だけを確認する |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 通知（利用者向け） | ヒットがあるとき、JSON の直下の `systemMessage` に `AI slop を検知: {NG の単語を・でつないだ並び}（{書き込みの名前}）` を返却する | 単語の並びは `additionalContext` の表の行の順と同じにする |
| 書き込みの名前 | 組み込みのツールはツール名、MCP ツールは `{プラグインの名前} の {ツール名}` | プラグインの名前の取り出し方はインターフェース定義設計で決める |
| 通知（エージェント向け） | `hookSpecificOutput.additionalContext` の NG と OK の表は変えない | - |
| 対象の MCP ツール | `MCP_TOOLS` に `dev-docs` のキーを加え、対象のツール名は `write_docs` にする。`project-index` のキーは残す | サーバーの部分 `plugin_dev-docs_dev-docs` が `dev-docs` を含む。`dev-docs-admin` に `write_docs` は無い |
| 規約を参照する案内 | `NOTICE_TAIL` に project-index と dev-docs の `search_docs` の完全名を並べる | 引数は変えない |
| hooks.json | `_description` に利用者の画面への 1 行の表示を加える | - |
| 設計書 | SC-148-1・IF-148-1・MOD-148-2 を、利用者向けの 1 行と、dev-docs と project-index の両方の名前に合わせる | - |
| テスト | 単体・結合テストに、`systemMessage` の 1 行と dev-docs の `write_docs` の照合のケースを加える | 既存の `additionalContext` の期待値は変えない |
| 既存機能への影響 | エージェント向けの通知と、書き込みを止めないこと・終了コード 0 は変わらない | - |

## 設計書の確定コミット

| 工程 | 範囲 | 補足 |
| --- | --- | --- |
| 単一ユースケース設計 | `fabdc4c..18bf2f3` | - |
| インターフェース定義設計 | `08b42c7..be305c7` | - |
