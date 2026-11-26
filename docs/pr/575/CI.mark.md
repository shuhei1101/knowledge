# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/interface/IF-352-1.yml.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/interface/IF-352-1.yml.yaml) | テストの全件実行のワークフロー | dev-docs の取り込みが要る場合に更新 |
| 実装 | [.github/workflows/test.yml](https://github.com/shuhei1101/knowledge/blob/develop/.github/workflows/test.yml) | テストの全件実行 | 同上 |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| テストの全件実行 | 結合の層で全ての文書の検査が Markdown のテンプレートの一致を確認できるよう、dev-docs を固定したコミットで入れる | ワークフローのファイルはインターフェース定義と一致させる（IF-72-3 の突き合わせ） |
