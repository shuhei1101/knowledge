# バックエンド

バックエンドの設定値一覧。

**ID**: CFG-1

## ファイル一覧

<!-- table: {"kind": "data", "columns": {"補足": {"width": {"mode": "nowrap"}}}} -->
| ファイル | 管理する値 | 補足 |
| --- | --- | --- |
| config/settings.yaml | 共通の設定値（秘匿情報を含む） | git 管理外 |
<!-- /table -->

## キー一覧

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| キー | 論理名 | ファイル | 型 | 必須 | 既定値 | 説明 | 反映 | 公開 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| port | 待受ポート | config/settings.yaml | int |  | 8765 | HTTP API の待受ポート | restart | user |
<!-- /table -->
