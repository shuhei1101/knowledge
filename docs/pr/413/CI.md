# CI

## 現状

<!-- table: data -->

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/test-procedure/TP-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/docs/test-procedure/TP-72-1.yaml) | テスト実行方法 | TL-1 は ruff と pyright を `&&` でつなぐ。`tests/e2e/workflow/` を回す層が無い。更新対象 |
| ドキュメント | [docs/interface/IF-352-1.yml.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/docs/interface/IF-352-1.yml.yaml) | テストの全件実行のワークフロー | `test_file` が `tests/e2e/workflow/test_test_yml.py`。変更しない（結合テストが失敗して workflow を直す場合だけ更新する） |
| ドキュメント | [docs/dev-command/CMD-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/docs/dev-command/CMD-72-1.yaml) | 開発コマンド | 静的検査は `TP-72-1#layers[lint]` を指す。actionlint の入れ方が案 B のときだけ環境構築を更新する |
| 実装 | [.github/workflows/pages.yml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/.github/workflows/pages.yml)・[.github/workflows/test.yml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/.github/workflows/test.yml) | workflow | actionlint 1.7.12 で検査して指摘 0 件（2026-11-15、手元の PATH の actionlint）。指摘が出たら修正する |
| テスト | [tests/e2e/workflow/test_test_yml.py](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/tests/e2e/workflow/test_test_yml.py)・[tests/e2e/workflow/conftest.py](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/tests/e2e/workflow/conftest.py) | workflow の結合テスト（IF-352-1 の 4 フロー） | 未実行。検証用のブランチ `test-workflow/...` を push し、テストの後に削除する |

<!-- /table -->

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| TL-1 の全件実行 | ruff check・ruff format --check・pyright・actionlint を、どれかが失敗しても全てを回して終了コードを集約する 1 コマンドにする | actionlint の入れ方は `未確定`（[要件](./要件.md)） |
| TL-1 の説明と前提 | 検査の対象に `.github/workflows/` を加え、actionlint の入れ方を `prerequisites` に記載する | - |
| workflow の結合テストを回す層 | `location: local` で、`run_all` に `pytest tests/e2e/workflow`、`run_one` にファイル単位の実行を記載する | 層は `未確定`（[要件](./要件.md)）。`duration` は初回の実測で記載する |
| 結合テストの実行 | `tests/e2e/workflow/test_test_yml.py` の 4 件だけを手元で実行する。他の結合テスト（TL-3）は、TP-72-1 の記載だけの変更で壊れないため実行しない | 実行の前に、この範囲を reviewer に確認する |
