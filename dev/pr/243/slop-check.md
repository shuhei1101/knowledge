# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| 実装 | [plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json](https://github.com/shuhei1101/knowledge/blob/f82d8ad36e1bec0dd2176332d24f4da390c08bb0/plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json) | フックが照合に使用する対応表のコピー | 対応表に行を追加したら再生成する |
| 実装 | [scripts/build_word_list.py](https://github.com/shuhei1101/knowledge/blob/f82d8ad36e1bec0dd2176332d24f4da390c08bb0/scripts/build_word_list.py) | 対応表のコピーの作成 | 変更しない |
| 実装 | [plugins/slop-check/hooks/post-tool-use/slop_check.py](https://github.com/shuhei1101/knowledge/blob/f82d8ad36e1bec0dd2176332d24f4da390c08bb0/plugins/slop-check/hooks/post-tool-use/slop_check.py) | 書き込んだ中身の照合 | 変更しない |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 対応表のコピー | 対応表の行を追加した後に `scripts/build_word_list.py` で再生成し、`check_all.py` の対応表のコピーの一致の検査に合格させる | 手で編集しない |
| 回帰確認 | 単体テストの全件と、`check_all.py`・`tests/integration/scripts/`・`tests/integration/slop-check/` の結合テストを実行する | コードを変更しない |
