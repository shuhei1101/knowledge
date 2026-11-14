# 規約『VS Code 拡張機能の配布』に、拡張機能のアイコンを作って登録する決まりを追加する

## 概要

VS Code 拡張機能を作る人が、初めて公開する前にアイコンを作って `package.json` の `icon` に登録する手順を、規約『VS Code 拡張機能の配布』で参照できるようにする。

## 背景

[#349](https://github.com/shuhei1101/knowledge/issues/349) の要望。
規約『VS Code 拡張機能の配布』はバージョン・.vsix・公開・入れ替えの依頼・ID を定めているが、アイコンを定めていないため、アイコンの無いまま公開される（例: shuhei1101/mdmark の `ShuheiNishikawa.mdmark-vscode` は `package.json` に `icon` が無い）。
Marketplace は `package.json` の `icon` に SVG を受け付けず、128×128px 以上の PNG を求める。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
