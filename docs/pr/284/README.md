# ブラウザのスクリプトを .js で記載してよい例外を tsc を挟めないものに限り、生成した .js を commit して配るものは .ts で記載する

## 概要

単体 HTML のブラウザのスクリプトを記載する人が、生成した `.js` を commit すれば配れるもの（GitHub Pages・プラグインの同梱物・配布物）を `.ts` で記載し、`.js` で記載してよいのは tsc を挟めないものだけだと、規約から読み取れるようになる。

## 背景

[Issue #234](https://github.com/shuhei1101/knowledge/issues/234) の要望（移し元は [shuhei1101/ai-monitor#2427](https://github.com/shuhei1101/ai-monitor/issues/2427)）。
規約『ビルドレス原則』の `script-extension-02`「`.js` で書いてよいのは、ビルドせずにそのまま配るもの（GitHub Pages・モックのプレビューなど）だけ」が、git でそのまま配る同梱物（プラグインの雛形など）にも当たると解釈できてしまう。
[shuhei1101/mindmap#21](https://github.com/shuhei1101/mindmap/pull/21#issuecomment-5962770404) でプラグインに同梱するプレビューの雛形を `.js` で設計し、ユーザーから `.ts` を使用するよう指摘を受けた。
規約『tsc 運用』の `generated-js-gitignore-01` は、ビルドしない配信先（GitHub Pages・配布先）と共用する生成 `.js` を `.ts` と同じ階層へ commit すると定めており、GitHub Pages の扱いで二つの規約が食い違っている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | サブシステム「文書」の計画書 |
