# アプリの画面の表・ボード・グラフ・図・コメントは mdmark の部品のカスタム要素を使用する決まりを規約に入れる

## 概要

アプリの画面を実装する人が、表・ボード・グラフ・図・本文へのコメントを mdmark の部品のカスタム要素で組むことと、部品で足りない機能の扱いを規約から参照できるようにする。

## 背景

[Issue #598](https://github.com/shuhei1101/knowledge/issues/598) の要望。
mdmark の配布物に、アプリの画面へ配置する部品のカスタム要素（`<mdmark-table>`・`<mdmark-view>`・`<mdmark-graph>`・`<mdmark-param-graph>`・`<mdmark-map>`・`<mdmark-comments>`）が入った（[shuhei1101/mdmark#793](https://github.com/shuhei1101/mdmark/issues/793)・[shuhei1101/mdmark#797](https://github.com/shuhei1101/mdmark/issues/797)）。
knowledge の規約は、表を TanStack Table と shadcn/ui の Table で組み、チャートを shadcn/ui の Chart、マップを自前で組むと定めていて、mdmark の部品を使用する決まりが無い。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
