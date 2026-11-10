# dev/ を廃止して文書を docs/ 1 つにまとめ、ai-monitor#3307 と同じ構成へ移す

## 概要

knowledge の `dev/` を廃止し、設計書・設計書のスキーマのコピー・作業 PR の計画を `docs/`・`schemas/` へ移して、[shuhei1101/ai-monitor#3307](https://github.com/shuhei1101/ai-monitor/pull/3307) と同じ構成にする。

## 背景

[Issue #237](https://github.com/shuhei1101/knowledge/issues/237) の要望。

- ai-monitor#3307（マージ済み）の要件「AI Monitor 自身以外の全ての監視対象のプロジェクトも、この PR と同じ構成へ移す。」による
- ai-monitor#3307 のマージの後の AI Monitor は `dev/` を読まないため、`dev/` が残る間は `python -m ai_monitor.design_docs` の設計書の検証・Markdown の生成が動かない
- 設計書の参照をパスから ID へ書き換える v0.4.0 の変換は、ai-monitor#3307 の planner からの連絡（[変換を掛ける commit](https://github.com/shuhei1101/knowledge/issues/237#issuecomment-6747092857)）により、`dev/` の置き場所のまま ai-monitor の [f135cff63](https://github.com/shuhei1101/ai-monitor/commit/f135cff63c1f6b4089f3db4bfdc1b2cb5bcdcb71) の変換で掛ける

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の計画書 |
