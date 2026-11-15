# CI

## 現状

<!-- table: data -->

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/test-procedure/TP-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/docs/test-procedure/TP-72-1.yaml) | テスト実行方法 | TL-2・TL-3 が `location: runner` で `run_runner` を持つ。ランナーで回したことはまだ無い |
| ドキュメント | [docs/interface/IF-352-1.yml.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/docs/interface/IF-352-1.yml.yaml) | テストの全件実行のワークフロー | 入出力とフローは変えない |
| 実装 | [.github/workflows/test.yml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/.github/workflows/test.yml) | 入力 `layer` の層の全件をランナーで回す | skip の件数に差があれば修正対象 |
| 実装 | [tests/unit/](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/tests/unit) | 単体テスト | ランナーでだけ skip・失敗するテストがあれば修正対象 |
| 実装 | [tests/integration/](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/tests/integration) | 結合テスト | ランナーでだけ skip・失敗するテストがあれば修正対象 |
| スキーマ | [schemas/design/interface.schema.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/schemas/design/interface.schema.yaml) | インターフェース定義のスキーマ | `test_file` の description が 3 文で、`test_check_all.py::test_normal_when_repository_schemas` の 2 文以内の検査に通らない（[#391](https://github.com/shuhei1101/knowledge/pull/391) で入った）。修正対象 |

<!-- /table -->

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| ランナーでの実行 | 作業ブランチで TL-2・TL-3 の `run_runner` を 1 回ずつ実行し、ログを `テスト結果/` に置く | 規約の連絡事項の「結合テストは作業 PR で全件を実行しない」に対し、TL-3 の全件の実行はこの Issue の要望そのもので、手元の資源を使わずランナーで回す |
| 手元での実行 | 同じ commit で TL-2・TL-3 の `run_all` を実行し、ログを `テスト結果/` に置く | ランナーの結果と突き合わせる基準 |
| 突き合わせ | 層ごと・Python のバージョンごとに passed・skipped・failed の件数と、skip されたテストの名前を比べる | - |
| `test_file` の description | 句点を読点に替えて 2 文に収め、`scripts/build_templates.py` でテンプレート『インターフェース定義』を作り直す | 初回のランナーの TL-3 で fail した。手元でも同じく fail する develop の不具合で、ランナーと手元の差ではない |
| 差があったとき | ランナーで足りない道具・環境の差なら `test.yml` を、手元の環境に依存したテストならテストを修正し、IF-352-1・TP-72-1 と食い違わないようにする | 差が無ければ実装は変えない |

## テスト結果

TL-2・TL-3 を初めてランナーで回したため、同じ commit（`589d25f`）で `run_runner` と手元の `run_all` を両方回し、件数を比べた。
初回（`dfea23c`）の `run_runner` では TL-3 の `test_normal_when_repository_schemas` が fail した（`test_file` の description が 3 文）。description を直して回し直した。

### 単体

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| `tests/unit/`（Python 3.14） | 全実行 | 実行のみ | ✅ | ランナー・手元ともに 284 passed・0 skipped<br>`テスト結果/20261115163614_589d25f_単体テスト.log` |
| `tests/unit/slop-check/`（Python 3.12） | 全実行 | 実行のみ | ✅ | ランナー・手元ともに 39 passed・0 skipped<br>`テスト結果/20261115163614_589d25f_単体テスト.log` |

### 結合

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| `tests/integration/` | 全実行 | 実行のみ | ✅ | ランナー・手元ともに 61 passed・0 skipped<br>`テスト結果/20261115163614_589d25f_結合テスト.log` |

### lint

TL-1 で違反なし（`テスト結果/20261115163614_589d25f_lint.log`）。
