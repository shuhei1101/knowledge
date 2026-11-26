# 列見出し

表の列見出しの中身。見出しの文字（押すと並べ替え）と、絞り込み・固定のボタンを並べる。

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| ID | CMP-1 |
| 実装 | src/app/components/macros.html#header_controls |
| Storybook | Plan/HeaderControls |
<!-- /table -->

<!-- table: {"kind": "plain", "collapse": {"open": false}} -->
| 対応テストファイル |
| --- |
| `tests/integration/storybook/test_計画画面の部品.py` |
<!-- /table -->

## 引数

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| 名前 | 型 | 必須 | 既定値 | 説明 |
| --- | --- | --- | --- | --- |
| key | 文字列 | ✓ |  | 列のキー。並べ替え・絞り込み・固定の対象を指す |
| label | 文字列 | ✓ |  | 見出しの文字 |
| numeric | 真偽値 |  | false | 数値の列か。右揃えにする |
| filterable | 真偽値 |  | false | 絞り込みのボタンを出すか |
<!-- /table -->

## イベント

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| イベント | 発火の条件 | 通知する値 | 説明 |
| --- | --- | --- | --- |
| 並べ替え | 見出しの文字を押したとき | key（`data-sort`） | 使用する側が 既定 → 昇順 → 降順 → 既定 と巡る |
| 固定 | ピンのボタンを押したとき | key（`data-pin`） | 使用する側が押した列より左を横スクロールでも固定する |
<!-- /table -->

## 状態

<!-- table: {"kind": "data", "columns": {"状態": {"width": {"mode": "nowrap"}}}} -->
| ストーリー名 | 状態 | 上書きする引数 |
| --- | --- | --- |
| Text | 文字の列（絞り込みできる） | name: key、value: title<br>name: label、value: タイトル<br>name: filterable、value: true |
| Numeric | 数値の列（右揃えで、絞り込みのボタンを持たない） | name: key、value: created_at<br>name: label、value: 作成日時<br>name: numeric、value: true |
<!-- /table -->

## アクセシビリティ

- 絞り込み・固定のボタンは `aria-pressed` で押した状態を伝える
- アイコンだけのボタンに `{label} で絞り込む` などのスクリーンリーダー向けの名前を付ける
