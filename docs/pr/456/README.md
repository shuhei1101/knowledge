# AI Monitor v0.5.0 の配布物へ追従する

## 概要

knowledge を AI Monitor v0.5.0 の配布物に準拠させる。

## 背景

[Issue #431](https://github.com/shuhei1101/knowledge/issues/431) の要望。
AI Monitor が [v0.4.0..v0.5.0](https://github.com/shuhei1101/ai-monitor/compare/v0.4.0...v0.5.0) で配布物を更新し、配布先の反映作業（[shuhei1101/ai-monitor#3462](https://github.com/shuhei1101/ai-monitor/pull/3462)）で、リポジトリの直下の `mdmark.config.yaml` に AI Monitor が生成する図のノードの種類を記載するよう求めている。
knowledge の [ai-monitor-version.ini](https://github.com/shuhei1101/knowledge/blob/3a4bde93c2e2983d28a73025a331264c85b69984/ai-monitor-version.ini) は `v0.4.0` のままで、直下に `mdmark.config.yaml` は無い。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | 配布先の反映作業の一覧 |
