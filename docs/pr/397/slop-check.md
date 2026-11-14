# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| 実装 | [plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json](https://github.com/shuhei1101/knowledge/blob/28a6634ba8223f4984390a70173d4a56682b2222/plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json) | フックが参照する対応表のコピー | 更新対象 |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 対応表のコピー | `scripts/build_word_list.py` で再生成する | 手で編集しない |

## テスト結果

なし（ドキュメント修正で記入する）
