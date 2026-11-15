# CI

## 現状

<!-- table: data -->

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/test-procedure/TP-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/docs/test-procedure/TP-72-1.yaml) | テスト実行方法 | TL-1〜TL-3 に `location` が無い。更新対象 |
| ドキュメント | `docs/scenario/SC-352-1.yaml` | 開発者がランナーでテストの層の全件を実行する | 新規 |
| ドキュメント | `docs/interface/IF-352-1.yml.yaml` | テストの全件実行のワークフロー | 新規 |
| ドキュメント | [docs/architecture/ARCH-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/docs/architecture/ARCH-72-1.yaml) | アーキテクチャ図 | サブシステム CI の役割と GitHub Actions の目的が Pages への配信だけ。更新対象 |
| ドキュメント | [docs/layout/LAY-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/docs/layout/LAY-72-1.yaml) | フォルダ構成 | `.github/workflows/` と `tests/` の行。更新対象 |
| ドキュメント | [docs/nonfunctional/NFR-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/docs/nonfunctional/NFR-72-1.yaml) | 非機能要件 | CI の 1 回の所要時間は Pages の配信だけを扱う。変更しない。テストの workflow の `timeout-minutes` は IF-352-1 が判定フローチャート『タイムアウトの決め方』で決める |
| ドキュメント | [docs/dev-command/CMD-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/docs/dev-command/CMD-72-1.yaml) | 開発コマンド | テストの分類はテスト実行方法の全体（`TP-72-1#`）を指し、`run_runner` も含むため変更しない |
| 実装 | [.github/workflows/pages.yml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/.github/workflows/pages.yml) | GitHub Pages への配信 | 変更しない。テストを回す workflow は無い |
| 実装 | [pytest.ini](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/pytest.ini) | pytest の設定 | `strict = true` のため、マーカーを付ける場合は `markers` に登録する |

<!-- /table -->

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 層の実行場所 | TL-1 は `local`。TL-2・TL-3 は判定フローチャート『テストの実行場所』で判定する | `/mnt/c`・端末の設定・手元の常駐サーバーを使用するテストは現状調査で見つかっていない。TL-3 は npm の道具（markdownlint-cli2・textlint）を workflow の中で入れる |
| workflow | `runner` の層を `workflow_dispatch` だけで起動する workflow を作り、ログを成果物に上げる | 1 本の workflow が入力 `layer` で層を選ぶ（[IF-352-1](../../interface/IF-352-1.yml.yaml)） |
| `run_runner` | `gh workflow run` で起動し、`gh run watch` で待ち、`gh run view --log` でログを取得して、失敗したときもログを取得してから失敗で終える | - |
| 手元のコマンド | `run_all`・`run_one` を変えずに残す | - |
| 結合テスト | workflow のフローごとに `tests/e2e/workflow/` へ結合テストを作る | 規約『V字モデル』 |

## 設計書の確定コミット

| 工程 | 範囲 | 補足 |
| --- | --- | --- |
| 単一ユースケース設計 | `2f52fec..7f3f06d` | SC-352-1 |
| 単一ユースケース設計 | `4b90863..5cabf62` | レビューの指摘の修正 |
| インターフェース定義設計 | `5cabf62..10d638a` | IF-352-1・TP-72-1・ARCH-72-1 |
| インターフェース定義設計 | `2a84b92..2f1b2bf` | レビューの指摘の修正 |
| モジュール構成設計 | `a937480..2b00f33` | LAY-72-1。workflow はモジュール構成を持たない（IF-137-2 と同じく IF-352-1 が step・if・Action を定める） |

## テスト結果

### 単体

TL-2 の `run_all` を手元で回した。`.github/workflows/test.yml` が develop に無く `workflow_dispatch` で起動できないため、`run_runner` の代わりにした（理由はログの先頭にも記載）。

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| `tests/unit/`（Python 3.14） | 全実行 | 実行のみ | ✅ | 284 テスト pass<br>`テスト結果/20261115115931_3e01b8d_単体テスト.log` |
| `tests/unit/slop-check/`（Python 3.12） | 全実行 | 実行のみ | ✅ | 39 テスト pass<br>`テスト結果/20261115115931_3e01b8d_単体テスト.log` |

`test.yml` と IF-352-1 の突き合わせは、全ての文書の検査の `scripts/_workflow.py` の `check_workflows` を IF-352-1・IF-137-2 に適用して違反 0 件を確認した。

### 結合

結合テスト作成の工程で記入する。

### lint

| 層 | 結果 | 補足 |
| --- | --- | --- |
| TL-1 | ✅ | 違反 0 件・警告 12 件（既存の `tests/unit/scripts/` の pyright の警告で、今回の変更に無い）<br>`テスト結果/20261115115304_3e01b8d_lint.log` |
