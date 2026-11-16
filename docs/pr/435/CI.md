# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/test-procedure/TP-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/8b2f90afc280a0fb2683a878b03a3e17ea6b4bc0/docs/test-procedure/TP-72-1.yaml) | テスト実行方法 | TL-2 の `run_all` が 2 つの pytest を `&&` でつなぐ。更新対象 |
| ドキュメント | [docs/interface/IF-352-1.yml.yaml](https://github.com/shuhei1101/knowledge/blob/8b2f90afc280a0fb2683a878b03a3e17ea6b4bc0/docs/interface/IF-352-1.yml.yaml) | テストの全件実行のワークフロー | 制約は「`run_all` と同じコマンド」で、コマンドそのものを持たない。変更しない |
| 実装 | [.github/workflows/test.yml](https://github.com/shuhei1101/knowledge/blob/8b2f90afc280a0fb2683a878b03a3e17ea6b4bc0/.github/workflows/test.yml) | テストの全件実行の workflow | `unit` のコマンドが 2 つの pytest を `&&` でつなぎ、`{ ...; } 2>&1 \| tee test.log` で `set -o pipefail` のもとで回す。更新対象 |
| テスト | [tests/e2e/workflow/test_test_yml.py](https://github.com/shuhei1101/knowledge/blob/8b2f90afc280a0fb2683a878b03a3e17ea6b4bc0/tests/e2e/workflow/test_test_yml.py) | workflow の結合テスト（IF-352-1 の 4 フロー） | `layer: unit` のフロー（正常系・異常系（テストの失敗））が、変更するコマンドを回す |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| TL-2 の `run_all` | 2 つの pytest を `(rc=0; ... \|\| rc=1; ... \|\| rc=1; exit $rc)` で囲み、どちらかが失敗しても両方を回して終了コードを集約する | 各 pytest のコマンドは一字一句変えない。TL-1 の `run_all` と同じ構造 |
| `test.yml` の `unit` のコマンド | `run_all` と同じコマンドにし、出力を `2>&1 \| tee test.log` で書き出す | サブシェルの終了コードが `set -o pipefail` で step の成否になる |
| 結合テストの実行 | 判定フローチャート『結合テストの実行範囲』で決めた範囲を、実行の前に `### 結合テストの実行範囲` の表にして reviewer に確認する | - |
