# ai-monitor#3222 の設計書のスキーマの修正を schemas/design/ に移し、既存の設計書とテンプレートを合わせる

## 概要

- 設計書のスキーマの原本 `schemas/design/` を、規約『表し方の優先順位』に合わせた ai-monitor#3222 の修正と同じ構造にする
- knowledge の `dev/設計書/` の設計書と `docs/template/` の設計書のテンプレートを、修正したスキーマに合わせる

## 背景

[Issue #210](https://github.com/shuhei1101/knowledge/issues/210) の要望。

- [shuhei1101/ai-monitor#3222](https://github.com/shuhei1101/ai-monitor/pull/3222)（マージ済み）は、ai-monitor の設計書のスキーマのコピーを規約『表し方の優先順位』に合わせて修正した。原本の `schemas/design/` には未適用
- [#163](https://github.com/shuhei1101/knowledge/issues/163) の作業 PR [#201](https://github.com/shuhei1101/knowledge/pull/201) で、ユーザーの判断によりスコープから除外し（[確認のスレッド](https://github.com/shuhei1101/knowledge/pull/201#discussion_r4487966632)）、この Issue に切り出した
- `dev/設計書/` の設計書の図の移行は [#145](https://github.com/shuhei1101/knowledge/issues/145) から移した。シナリオの図は [#246](https://github.com/shuhei1101/knowledge/issues/246)、インターフェース定義の `flow` とモジュール構成の `diagrams[].diagram` は [#251](https://github.com/shuhei1101/knowledge/issues/251) へ切り出した（[計画への反映](https://github.com/shuhei1101/knowledge/issues/210#issuecomment-6777507893)）

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | develop へマージした後の設計書のスキーマのタグの作成 |
