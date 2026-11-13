# scenario

複合・単一ユースケースの正常・異常シナリオ

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [エージェントが knowledge の文書を書き込む](./SC-72-5.yaml) | `write_docs` で検査のスクリプトに合格した文書だけを書き込む |
| [エージェントが knowledge の文書を検索・取得する](./SC-72-4.yaml) | `search_docs` に `source: knowledge` を指定して文書を検索・取得する |
| [エージェントが書き込んだ中身の AI slop の単語を通知される](./SC-148-1.yaml) | 書き込むツールの中身を slop-check が対応表で照合し、書き込みを止めずに NG と OK の単語を通知する |
| [利用者が GitHub Pages で knowledge の公開文書を参照する](./SC-137-1.yaml) | master へのマージで公開の文書だけを HTML にして Pages へ配信し、ブラウザで参照する |
| [利用者が project-index に knowledge を登録する](./SC-72-2.yaml) | `/project-index:setup` の点検に合格したら `sources[]` に knowledge を登録する |
| [利用者が画面で knowledge の文書を参照する](./SC-72-3.yaml) | dev-docs の画面で `nav` から文書を開いて参照する |
| [開発者がスキーマから設計書のテンプレートを生成する](./SC-201-1.yaml) | 生成のコマンドで、設計書の種類のテンプレートの本文をスキーマから書き出す |
| [開発者が文書の違反を検査する](./SC-72-6.yaml) | CI で全ての文書にスキーマの検査と検査のスクリプトを適用する |
| [利用者が端末に knowledge を導入して規約を参照する](./SC-72-1.yaml) | project-index への登録から、dev-docs の画面と MCP での検索・取得まで |

<!-- /table -->
