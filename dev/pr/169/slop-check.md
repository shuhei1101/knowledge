# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| 実装 | [plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json](https://github.com/shuhei1101/knowledge/blob/develop/plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json) | フックが照合する対応表のコピー | `scripts/build_word_list.py` で作り直す |
| ドキュメント | [dev/設計書/インターフェース定義/slop-check/書き込んだ中身の照合.py.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%95%E3%82%A7%E3%83%BC%E3%82%B9%E5%AE%9A%E7%BE%A9/slop-check/%E6%9B%B8%E3%81%8D%E8%BE%BC%E3%82%93%E3%81%A0%E4%B8%AD%E8%BA%AB%E3%81%AE%E7%85%A7%E5%90%88.py.yaml) | 書き込んだ中身を対応表で照合して通知する | 案 B を採る場合だけ変更 |
| ドキュメント | [dev/設計書/モジュール構成/slop-check/slop_check.py.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%83%A2%E3%82%B8%E3%83%A5%E3%83%BC%E3%83%AB%E6%A7%8B%E6%88%90/slop-check/slop_check.py.yaml) | 照合の関数と型 | 案 B を採る場合だけ変更 |
| 実装 | [tests/integration/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/develop/tests/integration/slop-check/test_slop_check.py) | 照合の結合テスト | 案 B を採る場合だけ変更。案 A・C は実行のみ |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 対応表のコピー | 対応表の行を追加した後に `uv run --frozen --script scripts/build_word_list.py` で作り直し、正本と一緒に commit する | `check_all.py` がコピーと正本の一致を検査する |
| 照合 | 案 A・C では変更しない。案 B では対応表の行のヒットさせる範囲のキーに従い、1 単語の値だけを照合する | `未確定`（要件.md の `## 要望`） |
| E2E | 単一ユースケース『エージェントが書き込んだ中身の AI slop の単語を通知される』の E2E を実行のみで回す | - |

## テスト結果

なし
