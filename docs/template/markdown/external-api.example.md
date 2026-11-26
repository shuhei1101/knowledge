# OpenAI

OpenAI が提供する LLM・埋め込み・音声の API。

**ID**: API-1

**使用箇所**

- integrations/openai/

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 状態 | 済 |
| 確認日 | 2026-01-10 |
| 確認内容 | チャットの応答を 1 回取得した |
<!-- /table -->

## 現在のバージョン情報

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| API バージョン | v1（URL 埋め込み型） |
| 確認日 | 2026-07-24 |
<!-- /table -->

<!-- table: {"kind": "data"} -->
| 環境 | URL |
| --- | --- |
| 本番 | https://api.openai.com/v1 |
<!-- /table -->

**公式 URL**: https://openai.com/api/

**公式ドキュメント**: https://platform.openai.com/docs/api-reference

## 認証セットアップ

**認証方式**: Bearer トークン（API キー）

**取得手順**

<!-- steps -->

1. https://platform.openai.com/api-keys を開く
2. `Create new secret key` で API キーを作る
3. 作ったキーを記録する（再表示できない）

<!-- /steps -->

**環境変数**

- OPENAI_API_KEY

## レートリミット

<!-- table: {"kind": "data", "columns": {"補足": {"width": {"mode": "nowrap"}}}} -->
| 対象 | 上限 | 補足 |
| --- | --- | --- |
| gpt-4o-mini | 500 RPM / 200,000 TPM | tier 1 |
<!-- /table -->

**再試行**: 超過すると 429 を返却する。Exponential Backoff（1 秒 → 2 秒 → 4 秒）で最大 3 回再試行する。

## 課金単価

<!-- table: {"kind": "data"} -->
| 対象 | 単価 |
| --- | --- |
| gpt-4o-mini | 入力 $0.150 / 出力 $0.600（1M トークン） |
<!-- /table -->

**課金の公式ページ**: https://openai.com/api/pricing/

## エンドポイント

### POST /chat/completions

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| メソッド | POST |
| パス | /chat/completions |
| 用途 | チャット形式の LLM の応答を作る |
<!-- /table -->

#### リクエスト

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| パラメータ | 型 | 必須 | 既定 | 説明 | 制限 | 配置場所 |
| --- | --- | --- | --- | --- | --- | --- |
| model | string | ✓ |  | モデル名 |  | body |
| messages | { role, content }[] | ✓ |  | チャットの履歴 |  | body |
| messages[].role | "system" or "user" or "assistant" | ✓ |  | 送信者の役割 |  | body |
| temperature | number |  | 1 | 応答のばらつき | 0〜2 | body |
<!-- /table -->

<!-- tabs -->

#### リクエスト例

```json
{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}]}
```

<!-- /tabs -->

#### レスポンス

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| フィールド | 型 | 説明 |
| --- | --- | --- |
| choices[].message.content | string | 生成されたテキスト |
| usage.prompt_tokens | number | 入力のトークン数 |
<!-- /table -->

#### ステータスコード

<!-- table: {"kind": "data", "columns": {"補足": {"width": {"mode": "nowrap"}}}} -->
| ステータスコード | 発生条件 | 補足 |
| --- | --- | --- |
| 200 | 正常 |  |
| 401 | API キーが不正 |  |
| 429 | レートリミットの超過 | Exponential Backoff で最大 3 回再試行する |
<!-- /table -->
