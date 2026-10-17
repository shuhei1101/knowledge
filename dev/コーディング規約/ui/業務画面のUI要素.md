# 業務画面のUI要素

業務系・管理画面に置く UI 要素と、その置き方・振る舞い。

## レイアウト

| 要素 | 置き方 | 出どころ |
| --- | --- | --- |
| ドロワー | 左から出す。開閉の起点はトップバーのハンバーガー。背景の押下と Esc で閉じる。スマホ幅では上タブの代わりにドロワーで画面を切り替える | [claude-balancer eb9be7a](https://github.com/shuhei1101/claude-balancer/commit/eb9be7a) |
| パンくず | 階層を遡れるリンク列にし、現在地はリンクにしない | - |

## ナビゲーション

| 要素 | 置き方 | 出どころ |
| --- | --- | --- |
| 上タブ | 画面の切り替えに使う。トップバーの直下に追従させて並べ、収まらないときはその帯の中で横スクロールする（トップバーの中では横スクロールさせない） | - |
| 横タブ | 画面内のサブナビに使う。本文の横に立て、幅が足りなければ本文の上へ寝かせる | [claude-balancer eb9be7a](https://github.com/shuhei1101/claude-balancer/commit/eb9be7a) |
| 検索 | トップバーから開き、見出しなどの単位で絞り込んでその位置へ移る | - |

## データ表示

<!-- table: data -->

| 要素 | 置き方 | 出どころ |
| --- | --- | --- |
| 列の並べ方 | 先頭列は人が読める識別子にする。列は重要な順に並べ、関連する列は隣に置く | [NN/g: Data Tables](https://www.nngroup.com/articles/data-tables/) |
| 文字と数値の揃え | 文字は左揃え、数値は右揃えで等幅数字にする。見出しは中身の揃えに合わせ、中央揃えにしない | [Pencil & Paper: Data Table Design](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-data-tables) |
| 表の並べ替え | 列見出しの押下で 昇順 → 降順 → 解除 を巡る。並べ替え中の列と向きを見出しに示す。解除すると既定の並びへ戻す。見出しには記号に加えて `aria-sort` を付ける | [MDN: aria-sort](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-sort) |
| 表の機能の出し分け | 表の大きさと用途で付ける機能を選ぶ。小さな表に並べ替え・絞り込みを付けない。既定は最小にする | [Material for MkDocs: Data tables](https://squidfunk.github.io/mkdocs-material/reference/data-tables/)・[MOJ Design System: Sortable table](https://design-patterns.service.justice.gov.uk/components/sortable-table/) |
| 表の絞り込み | 表の上に絞り込みの入力を置き、入力語で行を絞る | - |
| 絞り込みの件数 | 絞り込み中は全体の件数と残った件数を出す | [NN/g: Data Tables](https://www.nngroup.com/articles/data-tables/) |
| 列の絞り込み | 列の見出しから値を選んで絞る。適用中の条件を表の上にチップで並べ、個別解除と全解除を置く。選択肢に該当件数を出す | [Pencil & Paper: Filter UX](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-filtering) |
| 全体の検索 | 表の絞り込みとは別の入口にし、表に出していない範囲（過去の期間 等）まで引く。結果から行の詳細を開ける | - |
| 列のピン留め | 列見出しにピン留めボタンを置き、押した列とその左の列を横スクロールで固定する。固定は左から順に積む。もう一度押すと解除し、解除専用のボタンは置かない。固定中のボタンは押された見た目にする | - |
| 見出し行の固定 | 表が画面内にある間、見出し行を画面の上端（追従するヘッダーの直下）に留める | - |
| 固定の影 | 見出し行や列を固定している間は、固定した側の境に影を付け、流れる行や列の上に浮いていることを示す | [NN/g: Data Tables](https://www.nngroup.com/articles/data-tables/) |
| 列の表示切り替え | 列の一覧から表示を切り替える。行の識別子の列は外せない。既定に戻す操作を置く | [NN/g: Data Tables](https://www.nngroup.com/articles/data-tables/)・[Pencil & Paper: Data Table Design](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-data-tables)・[DataTables: colvis](https://datatables.net/reference/button/colvis) |
| 既定に戻す | 列の表示・並べ替え・固定を変えられる表には、既定に戻す操作を置く | [Pencil & Paper: Data Table Design](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-data-tables) |
| 保存ビュー | 絞り込み・並べ替え・列の組に名前を付けて保存し、呼び出せるようにする。保存先はサーバー（画面が書き込みの経路を持たないときはブラウザの保存（localStorage）） | [Shopify Polaris: Index filters](https://polaris-react.shopify.com/components/selection-and-input/index-filters) |
| 行の詳細 | 行の押下で外部のサイトへ飛ばさず、画面の中で詳細を開く。開き方は、隣の行と見比べられる非モーダルのサイドパネルを候補に入れて決める。外部のサイトへのリンクは詳細の中に置く。表に入れると 3 次元以上になる項目（行の項目が入れ子の表を持つ）は、行の開閉を既定にし、次の行に入れ子の表を開く。開閉で隠すのは 1 段だけにする。中身が大きいときは先頭だけを出し、全体はサイドの詳細で見せる | [NN/g: Data Tables](https://www.nngroup.com/articles/data-tables/) |
| 表以外の一覧 | ガントなど表以外の一覧でも、行の見出しを列に分け、表と同じピン留めで固定できるようにする | - |
| 狭い幅の表 | 列数の多い表は、狭い幅では後ろの列を畳み、行の押下で開く | - |
| 一覧のまとめて選ぶ操作 | 表を含む一覧の項目をまとめて選ぶ操作は、「全て選ぶ」「全て外す」の 2 つのボタンにせず、一覧の先頭に 1 つのチェックボックスで置く。全て選んでいれば選んだ状態、一部なら途中の状態（indeterminate）、1 つも選んでいなければ外した状態で出す。押すと、全て選んでいないときは全て選び、全て選んでいるときは全て外す | - |
| 表の一括操作 | 行を選んだら表の上に一括操作の帯を出し、選択件数と解除を置く。一括操作の間は行ごとの操作を止める | [Carbon: Data table](https://carbondesignsystem.com/components/data-table/usage/) |
| 表のコピー | 絞り込み・列の表示を反映した内容をコピーする | [Carbon: Data table](https://carbondesignsystem.com/components/data-table/usage/) |
| 行へのリンク | 行の識別子の列から、その行を指す URL を取れるようにする | - |

<!-- /table -->

## ガント・タイムライン

| 要素 | 置き方 | 出どころ |
| --- | --- | --- |
| 今日の線 | どの縮尺でも、日付の境目ではなく現在時刻の位置に引く | - |
| 縮尺 | 日・週・月の段階で選べるようにし、粗い縮尺ほど目盛りの表記を省略する。選んだ縮尺は保持する | - |
| 開いたときの位置 | 今日が左寄りに入る位置から表示する | - |

## アクション

| 要素 | 置き方 | 出どころ |
| --- | --- | --- |
| Issue 起票ボタン | 読んでいる画面から起票できるボタンを置く | - |
| 行ごとの操作 | 3 つ未満なら行の中にアイコンボタンで出し、3 つ以上はメニューにまとめる | [Carbon: Data table](https://carbondesignsystem.com/components/data-table/usage/) |
| FAB | 主アクションがある画面にだけ置く（外部規約『[画面デザインの原則](./画面デザインの原則.md)』の主アクションのボタン）。トップへ戻るボタンの上に積む | [claude-balancer eb9be7a](https://github.com/shuhei1101/claude-balancer/commit/eb9be7a) |
| トップへ戻る | 画面の隅に留め、スクロールした後に出す | - |
| テーマ切替 | ライト / ダークを切り替えるボタンをトップバーに置く | - |

## PC 幅とスマホ幅の確認

| 要素 | 置き方 | 出どころ |
| --- | --- | --- |
| PC 幅とスマホ幅の確認 | 画面を作ったら PC 幅とスマホ幅の両方でスクリーンショットを撮って確かめる（必須）。スマホ幅は窓の幅だけでなく、端末の定義（幅・画素密度・タッチ・UA）ごと再現して撮る。狭い端末での見切れは最も狭い端末（iPhone SE の 320 x 568）で見る | - |

Playwright では端末の定義をそのままコンテキストへ渡す。

```python
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context(**playwright.devices["iPhone 14 Pro"])
```

chromium で開くと、幅・画素密度・タッチ・UA は同じ値になり、描画だけが実機の Safari と違う。
