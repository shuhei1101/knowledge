# AI slop の単語の対応表の「消す」の行の allow に「取り消」「打ち消」を追加し、「取り消し線」をヒットさせない

## 概要

エージェントが「取り消し」「取り消し線」「打ち消し線」を記載したとき、プラグイン slop-check が「消す」の NG として通知しなくなる。

## 背景

[Issue #383](https://github.com/shuhei1101/knowledge/issues/383) の要望。
対応表の行 `kesu`（消す）の `pattern` は、消の直前が仮名の「取り消し」「取り消し線」にもヒットし、`allow` を持たない。
[shuhei1101/dev-docs#206](https://github.com/shuhei1101/dev-docs/pull/206) で、テストのコメント「削除の page に取り消し線を付ける」がヒットとして残った。
dev-docs の画面設計と部品の設計が同じものを「取り消し線」と呼んでいるため、置き換えられなかった。
受付のレビューの任意の指摘（[task-reviewer のコメント](https://github.com/shuhei1101/knowledge/issues/383#issuecomment-6876843394)）を受け、同じ理由でヒットする「打ち消し」も `allow` に含める。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 対応表の計画書 |
| [slop-check](./slop-check.md) | 対応表のコピーの計画書 |
