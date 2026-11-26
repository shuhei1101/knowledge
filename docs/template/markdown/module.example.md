# 種別とSchema

種別の Schema を読み込んで種別の一覧と `$ref` の解決先を持ち、設計書のパスから種別を解決する。

**ID**: MOD-1

<!-- table: {"kind": "plain", "collapse": {"open": false}} -->
| 対応テストファイル |
| --- |
| `tests/unit/features/schemas/test_loader.py` |
<!-- /table -->

## 関数

### read_schema_files

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 論理名 | Schemaのファイルの読み込み |
| コンテナ | features/schemas/loader.py |
| ユースケース | 共通 |
| 役割 | 読み込み |
| 概要 | 作業ツリーの Schema のファイルを名前 → 中身で取得する |
| 種別 | 関数 |
<!-- /table -->

#### 引数

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| 引数名 | 論理名 | 型 | 必須 | 説明 |
| --- | --- | --- | --- | --- |
| root | リポジトリの直下 | Path | ✓ | Schema を持つリポジトリの直下 |
<!-- /table -->

#### 戻り値

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 型 | dict[str, str] |
| 説明 | ファイル名 → 中身 |
<!-- /table -->

#### 処理

<!-- steps -->

1. `{root}/{TEMPLATES_DIR}` の直下の `*{SCHEMA_SUFFIX}` をファイル名の順に UTF-8 で読み込んで返却する

<!-- /steps -->

#### 例外

<!-- table: {"kind": "data"} -->
| 例外名 | 発生条件 | メッセージ |
| --- | --- | --- |
| FileNotFoundError | `{root}/{TEMPLATES_DIR}` が無い | 標準のメッセージ |
<!-- /table -->

#### 単体テスト

<!-- table: {"kind": "data", "columns": {"概要": {"width": {"mode": "nowrap"}}}} -->
| テスト名 | 正常/異常 | 概要 | 条件 | Mock | 期待値 | 対応する例外 |
| --- | --- | --- | --- | --- | --- | --- |
| test_read_schema_files | 正常 | 直下の Schema だけを取得する | 直下に Schema 2 つと md 1 つ、下のフォルダに Schema 1 つ | なし（一時ディレクトリ） | 直下の Schema 2 つだけ |  |
| test_read_schema_files_when_missing | 異常 | フォルダが無い | `{root}/{TEMPLATES_DIR}` の無い一時ディレクトリ | なし（一時ディレクトリ） | `FileNotFoundError` | フォルダが無い |
<!-- /table -->
