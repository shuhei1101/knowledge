# ai-monitor の reviewer のチェックシート・規約・判定フローチャートのうち、AI Monitor を前提にしない観点を knowledge へ移行する

## 概要

手元のセッションとほかのプロジェクトのレビューで、ai-monitor の reviewer のレビュー観点と、一般の規約・判定フローチャートを knowledge から参照できるようにする。

## 背景

[Issue #267](https://github.com/shuhei1101/knowledge/issues/267) の要望。
1 回目の移行（[#170](https://github.com/shuhei1101/knowledge/issues/170)・[#223](https://github.com/shuhei1101/knowledge/pull/223)）は、ai-monitor の reviewer のチェックシートを対象にしていなかった。
reviewer のチェックシートの観点の大半は AI Monitor のエージェント・MCP のツール・ラベル・PR ドキュメントを前提にしないが、ai-monitor にしか無い。
1 回目で「維持」にした規約・判定フローチャートにも、一般の決まりと AI Monitor の手順が 1 ページに混ざっている文書がある。
話し合いの資料 A-150 で文書ごとに「移行」「一部移行」を判定し、D-422 で A-150 の判定のとおりに移すと決めた。
ai-monitor の側の削除と参照の変更は [shuhei1101/ai-monitor#3195](https://github.com/shuhei1101/ai-monitor/issues/3195) が受け持つ。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
