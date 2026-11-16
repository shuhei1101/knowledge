# CI

## 現状

<!-- table: {"kind": "data"} -->

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/test-procedure/TP-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/docs/test-procedure/TP-72-1.yaml) | テスト実行方法 | TL-1 は ruff と pyright を `&&` でつなぐ。`tests/e2e/workflow/` を回す層が無い。更新対象 |
| ドキュメント | [docs/interface/IF-352-1.yml.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/docs/interface/IF-352-1.yml.yaml) | テストの全件実行のワークフロー | `test_file` が `tests/e2e/workflow/test_test_yml.py`。変更しない（結合テストが失敗して workflow を直す場合だけ更新する） |
| ドキュメント | [docs/dev-command/CMD-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/docs/dev-command/CMD-72-1.yaml) | 開発コマンド | 静的検査は `TP-72-1#layers[lint]` を指す。actionlint は uv が入れるため変更しない |
| 実装 | [.github/workflows/pages.yml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/.github/workflows/pages.yml)・[.github/workflows/test.yml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/.github/workflows/test.yml) | workflow | `uvx --from actionlint-py==1.7.12.25 --with shellcheck-py==0.11.0.1 actionlint` で検査して指摘 0 件（2026-11-15。`-verbose` で shellcheck の検査が有効なことを確認）。指摘が出たら修正する |
| テスト | [tests/e2e/workflow/test_test_yml.py](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/tests/e2e/workflow/test_test_yml.py)・[tests/e2e/workflow/conftest.py](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/tests/e2e/workflow/conftest.py) | workflow の結合テスト（IF-352-1 の 4 フロー） | 未実行。検証用のブランチ `test-workflow/...` を push し、テストの後に削除する |

<!-- /table -->

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| TL-1 の全件実行 | ruff check・ruff format --check・pyright・actionlint を、どれかが失敗しても全てを回して終了コードを集約する 1 コマンドにする | `uvx --from actionlint-py==1.7.12.25 --with shellcheck-py==0.11.0.1 actionlint`（[要件](./要件.md)）。`shellcheck-py` が無いと actionlint は `run:` の shellcheck の検査を飛ばす |
| TL-1 の説明と前提 | 検査の対象に `.github/workflows/` を加え、actionlint の入れ方を `prerequisites` に記載する | - |
| workflow の結合テストを回す層 | `location: local` で、`run_all` に `pytest tests/e2e/workflow`、`run_one` にファイル単位の実行を記載する | TL-6（[要件](./要件.md)）。`duration` は初回の実測で記載する |
| 結合テストの実行 | `tests/e2e/workflow/test_test_yml.py` の 4 件だけを手元で実行する。他の結合テスト（TL-3）は、TP-72-1 の記載だけの変更で壊れないため実行しない | 実行の前に、この範囲を reviewer に確認する |

## 設計書の確定コミット

| 工程 | 範囲 | 補足 |
| --- | --- | --- |
| モジュール構成設計 | `99c4a8f..b4b05ab` | TP-72-1 の TL-1・TL-6 |
| モジュール構成設計 | `b4b05ab..c087850` | reviewer の任意の指摘の反映（TL-1 の shellcheck-py・TL-6 の前提） |

## テスト結果

### 単体

なし（TP-72-1 の記載と PR ドキュメントだけを変え、規約『V字モデル』で対応する単体テストが無い）

### 結合

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/e2e/workflow/test_test_yml.py](https://github.com/shuhei1101/knowledge/blob/a50af49/tests/e2e/workflow/test_test_yml.py) | 全実行 | 実行のみ | ✅ | 4 テスト pass（初回の実行）<br>`テスト結果/20261115201405_a50af49_結合テスト.log` |

### lint

| コマンド | 結果 | 補足 |
| --- | --- | --- |
| TL-1 の全件実行 | ✅ | ruff check・ruff format --check・pyright（0 errors）・actionlint（shellcheck を含む）が全て通る<br>`テスト結果/20261115195058_c087850_lint.log` |
