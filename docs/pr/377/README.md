# テンプレート『フォルダ構成』で、リポジトリの外を元にする複製と、git で管理する生成物・複製を記載できるようにする

## 概要

フォルダ構成の設計書を記載する人が、リポジトリの外を元にする複製の元と、git で管理する生成物・複製を、テンプレート『フォルダ構成』の決まりのとおりに記載できるようになる。

## 背景

[Issue #373](https://github.com/shuhei1101/knowledge/issues/373) の要望。
テンプレート『フォルダ構成』の `rules-01` は、生成物・複製・一時ファイルを `gitignore` に記載し、生成物・複製のエントリに `generated_from`（`path`・`command` が必須）を記載すると定める。
[shuhei1101/alias-inject#100](https://github.com/shuhei1101/alias-inject/pull/100) で、npm の tarball から取り出した外部ライブラリや AI Monitor の配布物から複製したテーマ（元がリポジトリの外）と、hooks モジュールが import するため git で管理する生成物・複製を、この決まりのとおりに記載できなかった。
knowledge 自身のフォルダ構成 `docs/layout/LAY-72-1.yaml` も、`generated_from` を持つ `docs/template/` などを git で管理しており、`gitignore` には入れていない。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
