# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| インターフェース定義 | [docs/interface/IF-148-1.py.yaml](https://github.com/shuhei1101/knowledge/blob/a09f1065b93231a685ea81883289e93aacb25960/docs/interface/IF-148-1.py.yaml) | slop-check のフック | 対応表のコピーを `${CLAUDE_PLUGIN_ROOT}` から参照する |
| モジュール構成 | [docs/module/MOD-148-2.py.yaml](https://github.com/shuhei1101/knowledge/blob/a09f1065b93231a685ea81883289e93aacb25960/docs/module/MOD-148-2.py.yaml) | slop-check のフックのモジュール | 更新対象 |
| 実装 | [plugins/slop-check/hooks/post-tool-use/slop_check.py](https://github.com/shuhei1101/knowledge/blob/a09f1065b93231a685ea81883289e93aacb25960/plugins/slop-check/hooks/post-tool-use/slop_check.py) | 対応表の照合と通知 | `_default_word_list` が読み込み先を決める |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 対応表の読み込み先 | 環境変数 `SLOP_CHECK_WORD_LIST` が指す対応表のコピーがあればそれを参照し、無ければプラグインのフォルダのコピーを参照する | 案と決定は [要件](./要件.mark.md) の `## 要望` |
| 環境変数の設定 | ユーザースコープの `~/.claude/settings.json` の `env` に、knowledge の develop のワークツリーの対応表のコピーの絶対パスを記載する | 反映作業『slop-check の対応表の場所の設定』 |

## 設計書の確定コミット

| 工程 | 範囲 | 補足 |
| --- | --- | --- |
| インターフェース定義設計 | `a9301d2..fcf5816` | IF-148-1 に環境変数 `SLOP_CHECK_WORD_LIST` の読み込み先を追加し、SC-148-1 に正常シナリオを追加 |
| モジュール構成設計 | `190111d..e41c899` | MOD-148-2 に `WORD_LIST_ENV` と `default_word_list` を追加し、MOD-148-1 の冒頭リードを修正 |

## テスト結果

### 単体

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/unit/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/c50ced7/tests/unit/slop-check/test_slop_check.py) | 全実行 | 変更 | ✅ | `default_word_list` の 4 件を追加。3.14 の全件 319 件・3.12 の 49 件 pass（ランナー）<br>`テスト結果/20261121180011_c50ced7_単体テスト.log`<br>lint: `テスト結果/20261121180011_c50ced7_lint.log` |

### 結合テストの実行範囲

[検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) の `### 結合テストの実行範囲` の表にまとめた。
