# interface

サブシステムの境界の入出力と正常系・異常系のフロー

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [公開文書の配信のワークフロー](./IF-137-2.yml.yaml) | develop への push で公開の文書の HTML を作り、YAML が無いことを確かめて GitHub Pages へ配信する |
| [Pages の成果物の作成](./IF-137-1.py.yaml) | 公開の文書だけを mdmark で 1 枚の HTML にまとめた、Pages の出力のフォルダを作る CLI |
| [全ての文書の検査](./IF-72-3.py.yaml) | 全ての文書にスキーマの検査と文書の違反の検査を当てる CLI |
| [対応表のコピーの作成](./IF-148-2.py.yaml) | 正本の対応表の YAML から、フックが読む JSON のコピーを書き出す |
| [文書の Markdown への変換](./IF-72-2.py.yaml) | converters の約束で、文書 1 件を group の階層を見出しにした Markdown にする |
| [文書の違反の検査](./IF-72-1.py.yaml) | validators の約束で、文書 1 件の違反を配列で返す |
| [設計書のテンプレートの生成](./IF-201-1.py.yaml) | 設計書のスキーマから、対応するテンプレートの文書の items を組み立てて書き出す CLI |
| [書き込んだ中身の照合](./IF-148-1.py.yaml) | PostToolUse で書き込んだ中身を対応表で照合し、ヒットした単語を additionalContext で通知する |

<!-- /table -->
