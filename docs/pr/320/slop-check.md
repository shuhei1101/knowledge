# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| 実装 | [plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json](https://github.com/shuhei1101/knowledge/blob/69184599e8273dc9533e83c65a2d7f788898f100/plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json) | フックが参照する対応表のコピー | 更新対象 |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 対応表のコピー | `scripts/build_word_list.py` で再生成する | 手で編集しない |

## テスト結果

コードを変更せず、照合と対応表のコピーの作成の入出力も変わらないため、規約『V字モデル』の対応表で関係する単体・結合テストは無い。
追加した `examples.pass` の照合と、対応表とコピーの一致は `check_all.py` が検査し、違反 0 件で合格した（`テスト結果/20261113200800_48a148d_lint.log`）。
