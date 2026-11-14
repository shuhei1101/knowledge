# slop-check のフックの検知の画面表示・SKILL.md の生成・dev-docs と project-index の MCP の名前の両対応をまとめて行う

## 概要

利用者が slop-check のフックの検知した AI slop の単語を Claude Code の画面で 1 行で確認でき、スキル text-review の SKILL.md が設計書から生成され、slop-check のフックとスキル text-review が dev-docs と project-index のどちらの MCP の名前でも動くようにする。

## 背景

[#334](https://github.com/shuhei1101/knowledge/issues/334) の束の要望で、[#248](https://github.com/shuhei1101/knowledge/issues/248)・[#312](https://github.com/shuhei1101/knowledge/issues/312)・[#313](https://github.com/shuhei1101/knowledge/issues/313) を 1 本の作業 PR で行う。

| Issue | 背景 |
| --- | --- |
| #248 | slop-check の PostToolUse のフックは、検知したことを `hookSpecificOutput.additionalContext` でエージェントにだけ通知し、利用者の画面には出ない |
| #312 | [#275](https://github.com/shuhei1101/knowledge/pull/275)（[#224](https://github.com/shuhei1101/knowledge/issues/224)）で `docs/skill/text-review.yaml` を `type: skill` の書式に記載し直したが、`skills/text-review/SKILL.md` は手書きのままで、同じ内容を 2 か所で持っている |
| #313 | [#300](https://github.com/shuhei1101/knowledge/pull/300) でツールの完全名を project-index の名前だけにしたため、dev-docs のプラグインが有効な端末では `write_docs` の照合が有効にならない。dev-docs から project-index へ切り替える途中も、どちらの名前でも動く必要がある |

3 つとも `slop_check.py` か `skills/text-review/SKILL.md` を触る。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [slop-check](./slop-check.md) | slop-check の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの計画書 |
| [文書](./文書.md) | 文書の計画書 |
