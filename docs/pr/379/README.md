# 規約『テストの種類と配置』に、規約『V字モデル』が定める非機能要件のテスト（tests/nfr/）を加える

## 概要

Python のテストを作る人が、規約『テストの種類と配置』だけを読んで、非機能要件のテストを `tests/nfr/` に配置して実行できるようにする。

## 背景

[Issue #374](https://github.com/shuhei1101/knowledge/issues/374) の要望。
規約『V字モデル』（`dev-v-model`）の対応表は非機能要件のテストの配置先を `tests/nfr/` / `tests/external/` と定めるが、規約『テストの種類と配置』（`python-testing-layers`）のファイル配置のツリーに `nfr/` が無い。
[shuhei1101/voice-paste#300](https://github.com/shuhei1101/voice-paste/pull/300#discussion_r4572232942) で、reviewer が `tests/nfr/` は `dev-v-model` どおりで、修正する先は knowledge の規約と判定した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
