# index.html の作り方

- 各画面の `index.html` は `_layout.html` を継承し、`<app-shell>` の中に画面の中身だけを書く。

ブロックの使い分け:

| ブロック  | 入れるもの                                                                                                                                        |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `title`   | `画面名 — アプリ名` で統一                                                                                                                        |
| `head`    | 画面固有 CSS の link。`screen.css` が無ければ省く                                                                                                 |
| `body`    | `<app-shell>` を 1 つ。その中に画面コンテンツ                                                                                                     |
| `scripts` | `screen.js` を読む `<script type="module">` 1 つだけ（`screen.ts` から `tsc` が生成した `.js`。ブラウザは `.ts` を読めないので必ず `.js` を指す） |

- インライン `<script>` ブロックや `onclick=` 属性は使わない（外部 `screen.js` + `addEventListener`）
- importmap / `modulepreload` の規約は `html/js/モジュール解決.md`
