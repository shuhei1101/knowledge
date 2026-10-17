# shared

html/shared の規約

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [components](./components.md) | ドメインをまたいで使う共通 UI の置き場所 |
| [core](./core.md) | 環境・定数・ルーティング等のコア値の置き場所 |
| [css](./css.md) | コンポーネントに属さない基盤スタイルの置き場所 |
| [fmt](./fmt.md) | 日付・数値・通貨などの整形関数の置き場所 |
| [lib](./lib.md) | 全画面で使う汎用ユーティリティ（フォーマッタ・ログ・WebSocket クライアント等）。 |
| [logger](./logger.md) | ログ出力を集約する。画面・共通層は `console.*` を直書きせず logger 経由で出す。 |
| [vendor](./vendor.md) | 外部依存を vendoring して固定する置き場所 |

<!-- /table -->
