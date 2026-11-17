# テスト実行方法 TP-72-1 の lint 層へ actionlint を追加し、workflow の結合テストを初めて実行して回す層を確定させる

## 概要

開発者とエージェントが、knowledge の lint の層で workflow のファイルを actionlint で検査でき、workflow の結合テストを回す層をテスト実行方法から引けるようになる。

## 背景

[Issue #412](https://github.com/shuhei1101/knowledge/issues/412) の束（[#370](https://github.com/shuhei1101/knowledge/issues/370)・[#409](https://github.com/shuhei1101/knowledge/issues/409)）。
[#368](https://github.com/shuhei1101/knowledge/pull/368) でテンプレート『テスト実行方法』に「`.github/workflows/` を持つリポジトリは `lint` 層に actionlint を含める」が入ったが、develop の [docs/test-procedure/TP-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/99c4a8fe22de9638b4e089ac480978cf8e65530a/docs/test-procedure/TP-72-1.yaml) の TL-1 は ruff と pyright だけを回す。
[#404](https://github.com/shuhei1101/knowledge/pull/404) で追加した `tests/e2e/workflow/test_test_yml.py` は、`workflow_dispatch` が develop にある workflow だけを起動できるため未実行で、回す層も無い（TL-6 の `run_all` は `未確定`）。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [CI](./CI.md) | CI の計画書 |
