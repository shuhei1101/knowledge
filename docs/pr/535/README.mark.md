# エージェントフローの calls[].server の説明と SKILL.md の生成の MCP のツールの出し方を一致させる

## 概要

エージェントフローのスキーマの `calls[].server` の説明と、SKILL.md の生成が `type: mcp` の呼ぶものを出す振る舞いを一致させる。

## 背景

[Issue #534](https://github.com/shuhei1101/knowledge/issues/534) の要望。
スキーマは「変換で、ツールの完全な名前（Claude Code では `mcp__{server}__{tool}`）を作る」としているが、SKILL.md の生成は ``MCP `{server}` の `{tool}` `` と参照のまま出す。
そのため、今のスキル（text-review・meme-register・meme-research）は `type: tool` に MCP のツールの完全な名前を記載している。
[#533](https://github.com/shuhei1101/knowledge/pull/533) のドキュメント修正の工程で見つかった。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理と、直し方 |
| [文書](./文書.mark.md) | 文書のサブシステム（エージェントフローのスキーマ・テンプレート）の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) | SKILL.md の生成（設計書・実装・テスト）の計画書 |
