# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| 実装 | [.github/workflows/docs-check.yml](https://github.com/shuhei1101/knowledge/blob/develop/.github/workflows/docs-check.yml) | PR ごとに全ての文書の検査を動かす | markdownlint・textlint・yamllint のステップを追加 |
| ドキュメント | [dev/設計書/インターフェース定義/ci/文書の検査のワークフロー.yml.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%95%E3%82%A7%E3%83%BC%E3%82%B9%E5%AE%9A%E7%BE%A9/ci/%E6%96%87%E6%9B%B8%E3%81%AE%E6%A4%9C%E6%9F%BB%E3%81%AE%E3%83%AF%E3%83%BC%E3%82%AF%E3%83%95%E3%83%AD%E3%83%BC.yml.yaml) | 文書の検査のワークフローのインターフェース定義 | ステップと失敗の条件を追加 |
| ドキュメント | [dev/設計書/シナリオ/単一ユースケース/開発者が文書の違反を検査する.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%82%B7%E3%83%8A%E3%83%AA%E3%82%AA/%E5%8D%98%E4%B8%80%E3%83%A6%E3%83%BC%E3%82%B9%E3%82%B1%E3%83%BC%E3%82%B9/%E9%96%8B%E7%99%BA%E8%80%85%E3%81%8C%E6%96%87%E6%9B%B8%E3%81%AE%E9%81%95%E5%8F%8D%E3%82%92%E6%A4%9C%E6%9F%BB%E3%81%99%E3%82%8B.yaml) | CI で全ての文書を検査するシナリオ | lint の検査の流れを追加 |
| ドキュメント | [dev/設計書/開発コマンド/開発コマンド.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E9%96%8B%E7%99%BA%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89/%E9%96%8B%E7%99%BA%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89.yaml) | 開発で使うコマンド | 検査の分類にコマンドを追加 |
| ドキュメント | [dev/設計書/外部ライブラリ/](https://github.com/shuhei1101/knowledge/tree/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E5%A4%96%E9%83%A8%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA) | 使う外部ライブラリ・CLI | markdownlint-cli2・textlint・yamllint を追加 |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| markdownlint | markdownlint-cli2 を CI で動かす。区切り線（`---`）・太字（MD036 など）を『Markdown 編集規約』に合わせて設定する | 1 文 1 行は日本語の「。」に対応するカスタムルールが要るため、対応できるかを外部ライブラリの調査で確かめる |
| textlint | textlint と textlint-rule-preset-ja-technical-writing を CI で動かす | 単語の対応表は slop-check（#135）が持つため、prh は入れない |
| yamllint | yamllint を CI で動かし、引用符の無い値の取り違え（`#` 以降がコメントになるなど）を検出する | 設定は `.yamllint.yaml` |
| 当てる範囲 | 要件.md の `### 検査ツール` の `未確定` の決定に合わせる | 案 A なら、文書の YAML を変換のスクリプトで Markdown にして当てるステップを追加する |
| 既存の違反 | 追加した検査で既存の文書に出る違反は、この PR で修正する。修正しきれないルールは設定で無効にし、理由をコメントで残す | ジョブが落ちたままマージしない |

## テスト結果

未実施。
