# scenario

複合・単一ユースケースの正常・異常シナリオ

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [エージェントが knowledge の文書を書き込む](./SC-72-5.yaml) | `write_docs` で検査のスクリプトを通してから文書を書き込む |
| [エージェントが knowledge の文書を検索・取得する](./SC-72-4.yaml) | `search_docs` に `source: knowledge` を渡して文書を検索・取得する |
| [エージェントが書き込んだ中身の AI slop の単語を通知される](./SC-148-1.yaml) | 書き込むツールの中身を slop-check が対応表で照合し、書き込みを止めずに NG と OK の単語を通知する |
| [利用者が GitHub Pages で knowledge の公開文書を読む](./SC-137-1.yaml) | master へのマージで公開の文書だけを HTML にして Pages へ配信し、ブラウザで読む |
| [利用者が dev-docs に knowledge を登録する](./SC-72-2.yaml) | `/dev-docs:setup` の点検を通して `sources[]` に knowledge を登録する |
| [利用者が画面で knowledge の文書を読む](./SC-72-3.yaml) | dev-docs の画面で `nav` から文書を開いて読む |
| [開発者がスキーマから設計書のテンプレートを生成する](./SC-201-1.yaml) | 生成のコマンドで、設計書の種類のテンプレートの本文をスキーマから書き出す |
| [開発者が文書の違反を検査する](./SC-72-6.yaml) | CI で全ての文書にスキーマの検査と検査のスクリプトを当てる |
| [利用者が端末に knowledge を導入して規約を引く](./SC-72-1.yaml) | dev-docs への登録から、画面と MCP での検索・取得まで |
| [利用者がマーケットプレイスからプラグイン knowledge を入れてスキルを呼ぶ](./SC-327-1.yaml) | マーケットプレイスからプラグイン knowledge を入れて、スキル text-review を呼ぶ |

<!-- /table -->
