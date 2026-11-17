# テスト実行方法の run_runner で、起動した run を API で参照できるまで待ってから gh run watch を呼ぶ

## 概要

テスト実行方法の `run_runner` を実行するエージェントが、起動直後の実行を 404 で参照できずに終わらず、ランナーの集計の行を受け取れるようにする。

## 背景

[Issue #467](https://github.com/shuhei1101/knowledge/issues/467) の要望。
テスト実行方法 TP-72-1 の `run_runner` は `gh workflow run` の直後に `gh run watch "$run_id"` を呼ぶため、実行がまだ GitHub の API で参照できない間は `failed to get run: HTTP 404` で終わる。
テスト実行方法のスキーマの `run_runner` の例と、スキーマから生成するテンプレートも同じ記載方法になっている。
[shuhei1101/project-index#139](https://github.com/shuhei1101/project-index/pull/139)（TP-1）と claude-balancer の TP-275-1 は、実行を API で参照できるまで待つ修正を入れ済み。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
