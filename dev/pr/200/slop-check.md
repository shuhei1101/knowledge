# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| 実装 | [plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json](https://github.com/shuhei1101/knowledge/blob/develop/plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json) | フックが照合する対応表のコピー | `scripts/build_word_list.py` で再生成する |
| ドキュメント | [dev/設計書/インターフェース定義/slop-check/書き込んだ中身の照合.py.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%95%E3%82%A7%E3%83%BC%E3%82%B9%E5%AE%9A%E7%BE%A9/slop-check/%E6%9B%B8%E3%81%8D%E8%BE%BC%E3%82%93%E3%81%A0%E4%B8%AD%E8%BA%AB%E3%81%AE%E7%85%A7%E5%90%88.py.yaml) | 書き込んだ中身を対応表で照合して通知する | 変更しない |
| ドキュメント | [dev/設計書/モジュール構成/slop-check/slop_check.py.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%83%A2%E3%82%B8%E3%83%A5%E3%83%BC%E3%83%AB%E6%A7%8B%E6%88%90/slop-check/slop_check.py.yaml) | 照合の関数と型 | 変更しない。`pattern` の無い行は `ng` の文字列を部分一致で照合し、ヒットの開始位置を含む `allow` の出現があればそのヒットを除く |
| 実装 | [tests/integration/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/develop/tests/integration/slop-check/test_slop_check.py) | 照合の結合テスト | 実行のみ |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 対応表のコピー | 対応表の行を追加した後に `uv run --frozen --script scripts/build_word_list.py` で再生成し、原本と一緒に commit する | `check_all.py` がコピーと原本の一致を検査する |
| 照合 | 変更しない。ヒットさせる範囲は対応表の行の `pattern`・`allow` が持つ | - |
| E2E | 単一ユースケース『エージェントが書き込んだ中身の AI slop の単語を通知される』の E2E を実行のみで回す | - |

## テスト結果

コードは変更せず、対応表のコピーの再生成が既存のテストを壊さないかを回帰確認した。

### 単体

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/unit/slop-check/](https://github.com/shuhei1101/knowledge/tree/develop/tests/unit/slop-check) | 全実行 | 実行のみ | ✅ | 31 テスト pass（Python 3.12）<br>`テスト結果/20261106052216_24078cc_単体テスト.log` |

### 結合

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/integration/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/develop/tests/integration/slop-check/test_slop_check.py) | 全実行 | 実行のみ | ✅ | `テスト結果/20261106053150_24078cc_結合テスト.log` |
