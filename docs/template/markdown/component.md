# {タイトル}

{冒頭リード}

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| ID | {ID} |
| 実装 | {実装} |
| Storybook | {Storybook} |
<!-- /table -->

<!-- table: {"kind": "plain", "collapse": {"open": false}} -->
| 対応テストファイル |
| --- |
| `{対応テストファイル}` |
<!-- /table -->

## 引数

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| 名前 | 型 | 必須 | 条件 | 既定値 | 選択肢 | 受ける部品 | 有効になる条件 | 説明 | 状態 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {名前} | string / integer / number / boolean / enum / object / array / function / component | true / false | {条件} | {既定値} | {選択肢} | {受ける部品} | {有効になる条件} | {説明} | planned / implemented / deprecated / removed |
<!-- /table -->

## スロット

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| 名前 | 説明 | 差し込める部品 | スロットに渡る値 |
| --- | --- | --- | --- |
| {名前} | {説明} | {参照} | {スロットに渡る値} |
<!-- /table -->

## イベント

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| イベント | 発火の条件 | 通知する値 | 説明 |
| --- | --- | --- | --- |
| {イベント} | {発火の条件} | {通知する値} | {説明} |
<!-- /table -->

## CSS カスタムプロパティ

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| 名前 | 値の書式 | 既定値 | 説明 |
| --- | --- | --- | --- |
| {名前} | {値の書式} | {既定値} | {説明} |
<!-- /table -->

## 状態

<!-- table: {"kind": "data", "columns": {"状態": {"width": {"mode": "nowrap"}}}} -->
| ストーリー名 | 状態 | 照合で撮る | 上書きする引数 |
| --- | --- | --- | --- |
| {ストーリー名} | {状態} | true / false | name: {引数}、value: {値} |
<!-- /table -->

## 使用する部品

<!-- table: {"kind": "data"} -->
| 部品 | 使用方法 |
| --- | --- |
| {部品} | {使用方法} |
<!-- /table -->

## アクセシビリティ

- {アクセシビリティ}

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 項目のパス | 関係の種類 | いつ参照するか | 対象のパス |
| --- | --- | --- | --- | --- |
| {相手の ID} | {項目のパス} | requires / references / replaces / part_of / change_together | {いつ参照するか} | {対象のパス} |
<!-- /table -->

**検討事項**

- {検討事項}

**状態**: planned / implemented / deprecated / removed

**公開範囲**: public / internal

**タグ**

<!-- table: {"kind": "data"} -->
| タグの名前 | 主題 |
| --- | --- |
| {タグの名前} | true / false |
<!-- /table -->

**別名**

- {別名}
