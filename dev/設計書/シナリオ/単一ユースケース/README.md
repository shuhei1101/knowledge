# 単一ユースケース

1 つの機能の正常・異常シナリオ

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [利用者が dev-docs に knowledge を登録する](./利用者が dev-docs に knowledge を登録する.yaml) | `/dev-docs:setup` の点検を通して `sources[]` に knowledge を登録する |
| [利用者が画面で knowledge の文書を読む](./利用者が画面で knowledge の文書を読む.yaml) | dev-docs の画面で `nav` から文書を開いて読む |
| [エージェントが knowledge の文書を検索・取得する](./エージェントが knowledge の文書を検索・取得する.yaml) | `search_docs` に `source: knowledge` を渡して文書を検索・取得する |
| [エージェントが knowledge の文書を書き込む](./エージェントが knowledge の文書を書き込む.yaml) | `write_docs` で検査のスクリプトを通してから文書を書き込む |
| [開発者が文書の違反を検査する](./開発者が文書の違反を検査する.yaml) | CI で全ての文書にスキーマの検査と検査のスクリプトを当てる |
| [利用者が GitHub Pages で knowledge の公開文書を読む](./利用者が GitHub Pages で knowledge の公開文書を読む.yaml) | master へのマージで公開の文書だけを HTML にして Pages へ配信し、ブラウザで読む |

<!-- /table -->
