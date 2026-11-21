# 既存のノウハウに、話題に出たとき案内される aliases と足りないタグを補う

## 概要

既存のノウハウが、会話や本文で呼び名が出たときに案内され、タグの検索でもヒットするようになる。

## 背景

[Issue #551](https://github.com/shuhei1101/knowledge/issues/551) の要望。
[PR #550](https://github.com/shuhei1101/knowledge/pull/550) で、規約『ドキュメント管理』の `knowhow-01` に、ノウハウは rules.yaml に掲載せず `aliases` とタグで届けると追記した。
develop の `docs/knowhow/` のノウハウは、どれも `aliases` を持たず、呼び名が出ても案内されない。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書のサブシステムの計画書 |
