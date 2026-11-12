# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/scenario/SC-148-1.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/scenario/SC-148-1.yaml) | エージェントが書き込んだ中身の AI slop の単語を通知される | 103 行の分岐の説明が dev-docs の `write_docs` |
| ドキュメント | [docs/interface/IF-148-1.py.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/interface/IF-148-1.py.yaml) | 書き込んだ中身の照合 | 126・145 行のテストの入力、300・301 行の対象のツールと見分ける単語 |
| ドキュメント | [docs/module/MOD-148-2.py.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/module/MOD-148-2.py.yaml) | slop-check のモジュール構成 | 60 行の `MCP_TOOLS` のキー、95 行の `NOTICE_TAIL`、197・203 行の `is_target` のテストの条件 |
| 実装 | [plugins/slop-check/hooks/post-tool-use/slop_check.py](https://github.com/shuhei1101/knowledge/blob/develop/plugins/slop-check/hooks/post-tool-use/slop_check.py) | 書き込んだ中身の照合のフック | 36 行の `MCP_TOOLS`、100・102 行の `NOTICE_TAIL`、109 行のコメント |
| テスト | [tests/unit/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/develop/tests/unit/slop-check/test_slop_check.py) | 単体テスト | 173・190・214・233・276 行のツール名 |
| テスト | [tests/integration/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/develop/tests/integration/slop-check/test_slop_check.py) | 結合テスト | 144・158 行のツール名 |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 対象の MCP ツール | `MCP_TOOLS` のキー `dev-docs` を `project-index` にする。対象のツール名は `write_docs` のまま | サーバーの部分 `plugin_project-index_project-index` が `project-index` を含むため照合の対象に入る |
| 通知の文 | `NOTICE_TAIL` の `mcp__plugin_dev-docs_dev-docs__search_docs` を `mcp__plugin_project-index_project-index__search_docs` にする | 引数は変えない |
| 設計書 | SC-148-1・IF-148-1・MOD-148-2 のツールの完全名と MCP サーバーの名前を実装に合わせる | - |
| テスト | 単体・結合テストのツール名を `mcp__plugin_project-index_project-index__*` にする | 期待値は変えない |
| 既存機能への影響 | dev-docs の `write_docs` は照合の対象から外れる | project-index#15 で dev-docs から移ったため |

## 設計書の確定コミット

| 工程 | 範囲 | 補足 |
| --- | --- | --- |
| 単一ユースケース設計 | `3cea689..22ce503` | - |
| インターフェース定義設計 | `22ce503..e03bb58` | - |
| モジュール構成設計 | `e03bb58..9d2c133` | - |

## テスト結果

### 単体

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/unit/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/develop/tests/unit/slop-check/test_slop_check.py) | 全実行 | 変更 | ✅ | ツール名を project-index の完全名にした。Python 3.14 で `tests/unit` の 229 テスト、Python 3.12 で `tests/unit/slop-check` の 31 テストが pass<br>`テスト結果/20261112223744_ab66309_単体テスト.log` |

### lint

| 検査 | 結果 | 補足 |
| --- | --- | --- |
| ruff check・ruff format --check・pyright | ✅ | 違反 0 件（pyright の warning 10 件は作業 PR が変えていないファイル）<br>`テスト結果/20261112224354_a1528bd_lint.log`<br>`テスト結果/20261112223744_ab66309_lint.log` |

### 結合

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/integration/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/develop/tests/integration/slop-check/test_slop_check.py) | 全実行 | 変更 | ✅ | `test_normal_when_mcp_tool`・`test_normal_when_tool_not_target` のツール名を project-index の完全名にした。10 テスト pass<br>`テスト結果/20261112224354_a1528bd_結合テスト.log` |
