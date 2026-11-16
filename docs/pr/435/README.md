# テスト実行方法 TP-72-1 の TL-2 の全件実行を、前の pytest が失敗しても後の pytest を回して終了コードを集約する形にする

## 概要

開発者とエージェントが TL-2（単体テスト（バック））の全件実行で、Python 3.14 の `tests/unit` が失敗しても Python 3.12 の `tests/unit/slop-check` の結果まで受け取れるようになる。

## 背景

[Issue #416](https://github.com/shuhei1101/knowledge/issues/416) の要望。
develop の [docs/test-procedure/TP-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/8b2f90afc280a0fb2683a878b03a3e17ea6b4bc0/docs/test-procedure/TP-72-1.yaml) の TL-2 の `run_all` と、同じコマンドを回す [.github/workflows/test.yml](https://github.com/shuhei1101/knowledge/blob/8b2f90afc280a0fb2683a878b03a3e17ea6b4bc0/.github/workflows/test.yml) の `unit` は、2 つの pytest を `&&` でつなぎ、前の pytest が失敗すると後の pytest を回さない。
テンプレート『テスト実行方法』の `layers` の決まり（どれかが失敗しても全てを最後まで回し、終了コードを集約する）から逸脱している。
[#413](https://github.com/shuhei1101/knowledge/pull/413) で TL-1 の `run_all` を同じ構造にしたときに、スコープ外として切り出した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [CI](./CI.md) | CI の計画書 |
