# 規約『E2E テスト（Playwright）』の tests/e2e/ のツリーを、規約『V字モデル』の複合・単一ユースケースの分け方に合わせる

## 概要

TypeScript の E2E テストを作る人が、規約『V字モデル』と同じ `複合ユースケース/`・`単一ユースケース/` の分け方で Playwright の spec を配置できるようになる。

## 背景

[Issue #388](https://github.com/shuhei1101/knowledge/issues/388) の要望。
規約『E2E テスト（Playwright）』の `folder-responsibility-01` は `tests/e2e/` の下を `{domain}/`・`usecases/` で分け、規約『V字モデル』の `mapping-01` の `tests/e2e/複合ユースケース/`・`tests/e2e/単一ユースケース/` と食い違っている。
[#380](https://github.com/shuhei1101/knowledge/issues/380) の受付のレビューで挙がり、Python の規約だけを扱う [#386](https://github.com/shuhei1101/knowledge/pull/386) のスコープ外として切り出した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書のサブシステムの計画書 |
