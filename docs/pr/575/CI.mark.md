# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/interface/IF-352-1.yml.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/interface/IF-352-1.yml.yaml) | テストの全件実行のワークフロー | 変えない |
| 実装 | [.github/workflows/test.yml](https://github.com/shuhei1101/knowledge/blob/develop/.github/workflows/test.yml) | テストの全件実行 | step の構成は変えない |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| テストの全件実行 | 「層の全件を回す」の step の `unit`・`integration` のコマンドを、テスト実行方法の単体・結合の層の `run_all` と同じにする（固定したコミットの dev-docs を `--with` で加える）。step の構成と起動の条件は変えない | IF-352-1 は変えない |

## テスト結果

ドキュメント修正（テスト実行方法）だけで、対応する単体・結合テストは無い。
