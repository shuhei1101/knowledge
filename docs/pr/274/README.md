# knowledge のフォルダ構成の設計書（layout）を作成し、repository.layout・directory の内容を移す

## 概要

knowledge のフォルダ構成の設計書をテンプレート『フォルダ構成』（layout）の書式で作り、フォルダ構成の問題をレビューで洗い出せるようにする。

## 背景

[Issue #220](https://github.com/shuhei1101/knowledge/issues/220) の要望。knowledge にはフォルダ構成の設計書が無く、フォルダ構成の問題をレビューで洗い出せない。
テンプレートは [#219](https://github.com/shuhei1101/knowledge/issues/219)（PR [#265](https://github.com/shuhei1101/knowledge/pull/265)）で追加し、設計の手順の工程は [shuhei1101/ai-monitor#3267](https://github.com/shuhei1101/ai-monitor/issues/3267) で追加した。
#265 で廃止したキー（アーキテクチャ図の `repository.layout`・モジュール構成の `directory`）の knowledge の設計書の内容は、移し先が無いため [#265 から回された](https://github.com/shuhei1101/knowledge/issues/220#issuecomment-6792552163)。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | サブシステム「文書」の計画書 |
