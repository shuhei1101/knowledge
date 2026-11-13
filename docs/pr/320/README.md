# AI slop の単語の対応表の「返す」の行の allow に「折り返」を追加し、「折り返す」をヒットさせない

## 概要

エージェントが「折り返す」を記載したとき、プラグイン slop-check が「返す」の NG として通知しなくなる。

## 背景

[Issue #314](https://github.com/shuhei1101/knowledge/issues/314) の要望。
対応表の行 `kaesu`（返す）の `pattern` は「折り返す」「折り返した」にもヒットし、`allow` には「繰り返」だけが入っている。
[shuhei1101/dev-docs#188](https://github.com/shuhei1101/dev-docs/pull/188) で docstring の「幅で折り返した行の数」がヒットし、「返却する」「改行する」のどちらにも置き換えられなかった（[レビューの指摘](https://github.com/shuhei1101/dev-docs/pull/188#discussion_r4557542300)）。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 対応表の計画書 |
| [slop-check](./slop-check.md) | 対応表のコピーの計画書 |
