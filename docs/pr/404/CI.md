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
| ドキュメント | [docs/nonfunctional/NFR-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/docs/nonfunctional/NFR-72-1.yaml) | 非機能要件 | CI の 1 回の所要時間は Pages の配信だけを扱う。テストの workflow のタイムアウトを持たせるかをモジュール構成設計で決める |
| ドキュメント | [docs/dev-command/CMD-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/docs/dev-command/CMD-72-1.yaml) | 開発コマンド | テストの分類はテスト実行方法の全件実行を指す。`run_runner` を指すかをモジュール構成設計で決める |
| 実装 | [.github/workflows/pages.yml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/.github/workflows/pages.yml) | GitHub Pages への配信 | 変更しない。テストを回す workflow は無い |
| 実装 | [pytest.ini](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/pytest.ini) | pytest の設定 | `strict = true` のため、マーカーを付ける場合は `markers` に登録する |

<!-- /table -->

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 層の実行場所 | TL-1 は `local`。TL-2・TL-3 は判定フローチャート『テストの実行場所』で判定する | `/mnt/c`・端末の設定・手元の常駐サーバーを使用するテストは現状調査で見つかっていない。TL-3 は npm の道具（markdownlint-cli2・textlint）を workflow の中で入れる |
| workflow | `runner` の層を `workflow_dispatch` だけで起動する workflow を作り、ログを成果物に上げる | 1 本にするかは `要件.md` の `未確定` |
| `run_runner` | `gh workflow run` で起動し、`gh run watch` で待ち、`gh run view --log` でログを取得して、失敗したときもログを取得してから失敗で終える | - |
| 手元のコマンド | `run_all`・`run_one` を変えずに残す | - |
| 結合テスト | workflow のフローごとに `tests/e2e/workflow/` へ結合テストを作る | 規約『V字モデル』 |
