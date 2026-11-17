# 規約『GitHub Actions の workflow のテスト』の手順と E2E の conftest で、起動した実行を API で参照できるまで待ってから gh run watch を呼ぶ

## 概要

workflow のテストを記載・実行するエージェントが、起動直後の実行を 404 で参照できずに終わらず、実行の結論と step ごとの結論を受け取れるようにする。

## 背景

[Issue #477](https://github.com/shuhei1101/knowledge/issues/477) の要望。
規約『GitHub Actions の workflow のテスト』（`python-testing-workflow`）の steps-01 は、手順 2 で実行の ID を取り、手順 3 ですぐ `gh run watch {ID} --exit-status` を呼ぶ。
その実装の `tests/e2e/workflow/conftest.py` も、`_dispatch` で ID を取った直後に `_watch` で `gh run watch` を呼ぶ。
実行がまだ GitHub の API で参照できない間は `failed to get run: HTTP 404` で終わり、`check=False` のため続く `gh run view` も参照できず失敗する。
テスト実行方法の `run_runner` には [#476](https://github.com/shuhei1101/knowledge/pull/476)（起点 [Issue #467](https://github.com/shuhei1101/knowledge/issues/467)）で同じ待ちを入れ済みで、この作業 PR はそのスコープ外を受け持つ。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
| [CI](./CI.md) | CI の計画書（workflow の E2E テストの土台） |
