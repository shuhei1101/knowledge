# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/scenario/SC-148-1.yaml](https://github.com/shuhei1101/knowledge/blob/9b5d599/docs/scenario/SC-148-1.yaml) | エージェントが書き込んだ中身の AI slop の単語を通知される | 利用者の画面への 1 行の表示を、設定で表示するときだけにする |
| ドキュメント | [docs/interface/IF-148-1.py.yaml](https://github.com/shuhei1101/knowledge/blob/9b5d599/docs/interface/IF-148-1.py.yaml) | 書き込んだ中身の照合 | 入力に表示の設定を追加し、`systemMessage` を出す条件に加える |
| ドキュメント | [docs/module/MOD-148-2.py.yaml](https://github.com/shuhei1101/knowledge/blob/9b5d599/docs/module/MOD-148-2.py.yaml) | slop-check / hooks / slop_check.py | 設定を取得する関数と、`systemMessage` を組み立てる条件を追加する |
| 実装 | [plugins/slop-check/hooks/post-tool-use/slop_check.py](https://github.com/shuhei1101/knowledge/blob/9b5d599/plugins/slop-check/hooks/post-tool-use/slop_check.py) | 書き込んだ中身の照合のフック | 203 行目でヒットがあれば常に `systemMessage` を出す |
| 実装 | [plugins/slop-check/hooks/hooks.json](https://github.com/shuhei1101/knowledge/blob/9b5d599/plugins/slop-check/hooks/hooks.json) | slop-check のフックの登録 | `_description` の `systemMessage` の記述を、設定で表示するときだけに合わせる |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 表示の設定 | 画面への 1 行の表示を切り替える設定を 1 つ追加し、値が無いときは表示しない | 配置先と名前は `未確定`（[要件](./要件.md)） |
| 通知の出力 | ヒットがあれば `additionalContext` は今のまま出し、`systemMessage` は設定が表示するときだけ出す | 設定の値を解釈できないときは表示しない |
| テスト | 単体は設定の取得と出力の分岐、結合は設定の有無ごとにフックを子プロセスで起動して出力を確認する | `tests/unit/slop-check/`・`tests/integration/slop-check/` |

## テスト結果

未実施。
