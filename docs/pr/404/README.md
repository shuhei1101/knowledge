# テスト実行方法の層ごとに実行場所を決め、ランナーで回せる層を GitHub Actions の workflow で回す

## 概要

開発者とエージェントが、knowledge のテストのうちランナーで回せる層を GitHub Actions のランナーで回せるようになる。

## 背景

[Issue #352](https://github.com/shuhei1101/knowledge/issues/352) の要望。
全てのプロジェクトの単体・結合テストが同じ WSL の上で走り、メモリが足りなくなっている。
develop の [docs/test-procedure/TP-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/2f52fec0ca6db9cf9f68da711011a0bf06151fce/docs/test-procedure/TP-72-1.yaml) は全ての層を手元で回す前提で、層の実行場所（`location`）を持たない。
`.github/workflows/` にテストを回す workflow は無い。

前提の [#350](https://github.com/shuhei1101/knowledge/issues/350)・[#351](https://github.com/shuhei1101/knowledge/issues/351)・[shuhei1101/ai-monitor#3434](https://github.com/shuhei1101/ai-monitor/issues/3434) は入っている（[ユーザーのコメント](https://github.com/shuhei1101/knowledge/issues/352#issuecomment-6884759082)）。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [CI](./CI.md) | CI の計画書 |
