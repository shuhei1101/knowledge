# react-image-crop

React 用の画像トリミング（クロップ）UI ライブラリ。
選択範囲のプレビューを提供し、トリミング後の画像を Blob / dataURL で出す。

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| ID | LIB-1 |
| 種類 | ライブラリ |
| 識別子 | pkg:npm/react-image-crop |
| 依存の範囲 | 必須 |
| 採用状態 | 採用 |
<!-- /table -->

**使用箇所**

- components/AvatarCropModal.tsx

**上流リポジトリ**: DominicTobias/react-image-crop

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 状態 | 済 |
| 確認日 | 2026-07-24 |
| 確認内容 | 円形の選択とプレビューを最小のコードで動かした |
<!-- /table -->

## 現在のバージョン情報

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| バージョン | 11.0.5 |
| 最新版 | 11.0.5 |
| 確認日 | 2026-07-24 |
| バージョンの出所 | package.json |
| バージョンの固定方法 | 完全一致で固定 |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| ライセンス | ISC |
| 公式 URL | https://github.com/DominicTobias/react-image-crop |
| 公式ドキュメント | https://github.com/DominicTobias/react-image-crop#readme |
<!-- /table -->

## インストール手順

```bash
npm install react-image-crop@11.0.5
```

CSS の読み込みも要る。

```ts
import "react-image-crop/dist/ReactCrop.css";
```

## API

**バージョン**: 11.0.5

### centerCrop

**種別**: 関数

**用途**: クロップ範囲を画像の中央に配置する

#### パラメータ

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| crop | Crop | ✓ | 中央に配置したいクロップ範囲 |
| mediaWidth | number | ✓ | 画像の幅（px） |
| mediaHeight | number | ✓ | 画像の高さ（px） |
<!-- /table -->

<!-- tabs -->

#### パラメータ例

```ts
const initial = centerCrop({ unit: "%", x: 0, y: 0, width: 50, height: 50 }, 1280, 720);
```

<!-- /tabs -->

#### 戻り値

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| フィールド | 型 | 説明 |
| --- | --- | --- |
| - | Crop | 中央に配置したクロップ範囲 |
<!-- /table -->

## 不具合一覧

### onCrop が初回マウント時に発火しない

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 概要 | 初期値を指定しても最初の 1 回だけコールバックが呼ばれない |
| 発生日 | 2026-08-02 |
| 状態 | 回避策あり |
| 概要 | `crop` に初期値を指定してマウントしても、`onCrop` が最初の 1 回だけ呼ばれない。 |
<!-- /table -->

- v11.0.0 以降
- `crop` を制御コンポーネントとして親から指定している

#### 対処法

<!-- table: {"kind": "data"} -->
| 方法 | 結果 | 推奨 |
| --- | --- | --- |
| マウント直後に親側で初期値を 1 度流す | 初回から値が一致する | ✓ |
| v10 系に固定する | 発火するが、v11 の性能改善を受け取れない |  |
<!-- /table -->
