# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [設計書/インターフェース定義/ci/文書の検査のワークフロー.yml.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%95%E3%82%A7%E3%83%BC%E3%82%B9%E5%AE%9A%E7%BE%A9/ci/%E6%96%87%E6%9B%B8%E3%81%AE%E6%A4%9C%E6%9F%BB%E3%81%AE%E3%83%AF%E3%83%BC%E3%82%AF%E3%83%95%E3%83%AD%E3%83%BC.yml.yaml) | PR ごとに全ての文書の検査を走らせるワークフローのインターフェース定義 | 参考（ランタイムの入れ方を揃える） |
| 実装 | [.github/workflows/docs-check.yml](https://github.com/shuhei1101/knowledge/blob/develop/.github/workflows/docs-check.yml) | 文書の検査のワークフロー | 変更なし |
| ドキュメント | `設計書/インターフェース定義/ci/公開文書の配信のワークフロー.yml.yaml`（新規） | Pages へ公開の文書を配信するワークフローのインターフェース定義 | 新規 |
| 実装 | `.github/workflows/pages.yml`（新規） | Pages へ公開の文書を配信するワークフロー | 新規 |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 起動の契機 | master への push と `workflow_dispatch` | develop・PR では動かさない |
| 権限 | `contents: read`・`pages: write`・`id-token: write` | Pages へのデプロイに要る最小の権限 |
| 同時実行 | `concurrency` を Pages の配信で 1 つにし、走っている配信は取り消さない | 途中で取り消すと配信が半端に終わる |
| ランタイム | Python・uv は文書の検査のワークフローと同じ入れ方にする。Node と mdmark を入れる | mdmark の入れ方は `未確定`（要件.md の `## 要望`） |
| 成果物を作る | 検査と変換のスクリプトの成果物を作るスクリプトを 1 回呼び、出力のフォルダを成果物にする | 失敗したら以降のステップを止める |
| 原本の混入の検査 | 成果物の中に `.yaml` が 1 つでもあれば、配信せずにジョブを失敗させる | 非公開の YAML が Pages から漏れないことを機械で守る |
| 配信 | `actions/upload-pages-artifact` と `actions/deploy-pages` で配信する | 配信元を Actions に切り替える反映作業が前提 |

## テスト結果
