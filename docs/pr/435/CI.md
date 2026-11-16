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

## 設計書の確定コミット

| 工程 | 範囲 | 補足 |
| --- | --- | --- |
| モジュール構成設計 | `8b2f90a..bfa48f6` | TP-72-1 の TL-2 の `run_all`。project-index の `write_docs` が作業ツリーから書き込めず（ai-monitor#3547 と同じ原因）、YAML を直接編集した |

## テスト結果

### 単体

なし（変更は TP-72-1 の記載と `.github/workflows/test.yml` の `run:` のコマンドだけで、規約『V字モデル』で対応する単体テストが無い）

### 結合テストの実行範囲

| 変更したファイル | 結果 | 実行する結合テスト | 結合テストが無い入口 |
| --- | --- | --- | --- |
| `.github/workflows/test.yml` | R7（TL-6 は IF-352-1 の `test_file`。TL-3 は参照する結合テストが無い） | `tests/e2e/workflow/test_test_yml.py::test_normal`・`tests/e2e/workflow/test_test_yml.py::test_error_when_tests_fail` | - |
| `docs/pr/435/CI.md` | R7（TL-3・TL-6） | - | - |
| `docs/pr/435/README.md` | R7（TL-3・TL-6） | - | - |
| `docs/pr/435/タスク一覧.yaml` | R7（TL-3・TL-6） | - | - |
| `docs/pr/435/テスト結果/20261117062531_1926f0b_lint.log` | R7（TL-3・TL-6） | - | - |
| `docs/pr/435/要件.md` | R7（TL-3・TL-6） | - | - |
| `docs/pr/435/要件.yaml` | R7（TL-3・TL-6） | - | - |
| `docs/test-procedure/TP-72-1.yaml` | R7（TL-3・TL-6） | - | - |

- `test.yml` は、`layer: unit` のときの「層の全件を回す」の `run:` だけを変えた。`layer: unit` で起動するフロー（正常系・異常系（テストの失敗））だけが変えたコマンドを通り、`layer: integration` の 2 フローは通らない
- TL-3 の [tests/integration/scripts/test_check_all.py](https://github.com/shuhei1101/knowledge/blob/1926f0b/tests/integration/scripts/test_check_all.py) は workflow をフィクスチャの `pages.yml` で検査し、`scripts/_workflow.py` の突き合わせも trigger・入力・`concurrency`・step の名前と `if` だけを比べ、`run:` の中身を比べないため影響しない
- `TP-72-1.yaml` と PR ドキュメントを参照する結合テストは無い
- 実行するコマンドは TL-6 の `run_one`（`location: local`）

### 結合

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/e2e/workflow/test_test_yml.py](https://github.com/shuhei1101/knowledge/blob/eb07184/tests/e2e/workflow/test_test_yml.py) | `test_normal`・`test_error_when_tests_fail` | 実行のみ | ✅ | 2 テスト pass<br>`テスト結果/20261117063431_eb07184_結合テスト.log`<br>`/tmp/pytest-of-shuhei2441` が root の所有で pytest の一時フォルダを作れなかったため、`TMPDIR` を `/tmp/ai-monitor-435-tmp` にして回した（コマンドは TL-6 の `run_one` のまま） |

### lint

| コマンド | 結果 | 補足 |
| --- | --- | --- |
| TL-1 の全件実行 | ✅ | ruff check・ruff format --check・pyright（0 errors）・actionlint（shellcheck を含む）が全て通る<br>`テスト結果/20261117062531_1926f0b_lint.log` |
