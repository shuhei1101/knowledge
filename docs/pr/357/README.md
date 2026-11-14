# 規約『VS Code 拡張機能の配布』に、Marketplace へ Trusted Publishing でタグから自動公開する決まりを追加する

## 概要

VS Code 拡張機能を作る人が、Marketplace への公開を長期のトークン無しにタグから自動で行う設定の手順を、規約『VS Code 拡張機能の配布』で参照できるようにする。

## 背景

[#353](https://github.com/shuhei1101/knowledge/issues/353) の要望。
規約『VS Code 拡張機能の配布』の `publish-01` は「自動にできる公開先は CI で公開し、できない公開先は手動で公開する」とだけ定め、自動で公開する設定のやり方を定めていない。
Marketplace は Trusted Publishing（GitHub Actions の OIDC）に対応しており、Marketplace へ公開するグローバル PAT は 2026-12-01 に廃止される。
shuhei1101/mdmark では shuhei1101/mdmark#512 で Trusted Publishing を設定した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
