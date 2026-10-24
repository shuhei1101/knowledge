# テンプレート: 外部API

利用する外部 API 1 つにつき 1 ファイル。そのプロジェクトで使うエンドポイントだけを公式ドキュメントから抜き出す。

## 項目

<!-- table: data -->

| 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | examples |
| --- | --- | --- | --- | --- | --- | --- | --- |
| title | タイトル | string | 必須 | - | - | API 名。ファイル名に合わせる。 | - |
| lead | 冒頭リード | string | - | - | - | API が何をするものかを 1〜3 行で要約する。自プロジェクトでの用途は書かない。<br>初回に書いた内容のまま保ち、後から情報を追加しない。 | - |
| used_in | 使用箇所 | array | - | - | - | 呼び出す境界層のパス（リポジトリの直下から）。 | - |
| verification | 動作確認 | object | - | - | - | 動かして確かめたか。 | - |
| verification.state | 状態 | string | 必須 | 済 / 未確認 | - | - | - |
| verification.date | 確認日 | string | - | - | pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ | `YYYY-MM-DD`。 | - |
| verification.detail | 確認内容 | string | - | - | - | 確かめた内容か、確かめられない理由。 | - |
| version | 現在のバージョン情報 | object | 必須 | - | - | - | - |
| version.api_version | API バージョン | string | 必須 | - | - | header 指定型か URL 埋め込み型かを添える。 | - |
| version.checked_on | 確認日 | string | 必須 | - | pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ | - | - |
| version.sunset | 廃止予定日 | string | - | - | - | - | - |
| base_urls | ベース URL | array | - | - | minItems: 1 | - | - |
| base_urls[].env | 環境 | string | 必須 | - | - | - | - |
| base_urls[].url | URL | string | 必須 | - | - | - | - |
| official_url | 公式 URL | string | - | - | - | - | - |
| docs_url | 公式ドキュメント | string | - | - | - | - | - |
| terms_url | 利用規約 | string | - | - | - | - | - |
| contact | 連絡先 | string | - | - | - | - | - |
| status_page | 障害情報の確認先 | string | - | - | - | - | - |
| auth | 認証セットアップ | object | 必須 | - | - | - | - |
| auth.method | 認証方式 | string | 必須 | - | - | Bearer / API Key Header / OAuth2 / JWT 等。 | - |
| auth.scopes | スコープ | array | - | - | - | - | - |
| auth.steps | 取得手順 | string | - | - | - | キー取得の公式ページの URL と番号付きの手順。 | - |
| auth.env_vars | 環境変数 | array | - | - | - | `.env.example` と一致させる。 | - |
| auth.usage | リクエスト時の利用 | string | - | - | - | コードブロック。 | - |
| rate_limits | レートリミット | array | - | - | - | - | - |
| rate_limits[].target | 対象 | string | 必須 | - | - | - | - |
| rate_limits[].limit | 上限 | string | 必須 | - | - | 単位（RPM / TPM 等）を付ける。 | - |
| rate_limits[].notes | 補足 | string | - | - | - | - | - |
| retry | 再試行 | string | - | - | - | 超過時のステータスと再試行の方針（Retry-After・Exponential Backoff 等）。 | - |
| pricing | 課金単価 | array | - | - | - | - | - |
| pricing[].target | 対象 | string | 必須 | - | - | - | - |
| pricing[].price | 単価 | string | 必須 | - | - | - | - |
| pricing[].notes | 補足 | string | - | - | - | - | - |
| pricing_url | 課金の公式ページ | string | - | - | - | 課金単価を書くときは必ず持つ。 | - |
| error_format | エラー応答の形式 | string | - | - | - | Markdown で書く本文。<br>他の設計書を指すときは説明文の中にリンクを書かず、参照は `refs`（`ref` の配列）に持つ。 | - |
| pagination | ページングの方式 | string | - | - | - | Markdown で書く本文。<br>他の設計書を指すときは説明文の中にリンクを書かず、参照は `refs`（`ref` の配列）に持つ。 | - |
| timeout | タイムアウト | string | - | - | - | - | - |
| endpoints | エンドポイント | array | 必須 | - | minItems: 1 | このプロジェクトで使うエンドポイント。 | - |
| endpoints[].name | 名前 | string | 必須 | - | - | `{METHOD} {パス}`。パスはベース URL からの相対。 | - |
| endpoints[].method | メソッド | string | 必須 | GET / POST / PUT / PATCH / DELETE / HEAD / OPTIONS | - | - | - |
| endpoints[].path | パス | string | 必須 | - | - | - | - |
| endpoints[].summary | 用途 | string | 必須 | - | minLength: 1, pattern: ^[^\n]+$ | 1 行の用途。 | - |
| endpoints[].operation_id | 操作の識別子 | string | - | - | - | - | - |
| endpoints[].tags | 分類タグ | array | - | - | - | - | - |
| endpoints[].permissions | 必要な権限 | string | - | - | - | - | - |
| endpoints[].idempotent | 冪等 | boolean | - | - | - | - | - |
| endpoints[].description | 説明 | string | - | - | - | Markdown で書く本文。<br>他の設計書を指すときは説明文の中にリンクを書かず、参照は `refs`（`ref` の配列）に持つ。 | - |
| endpoints[].request | リクエスト | array | - | - | - | - | - |
| endpoints[].request[].name | パラメータ | string | 必須 | - | - | オブジェクトの子は `parent.child`、配列の要素の子は `parent[].child`。 | - |
| endpoints[].request[].type | 型 | string | 必須 | - | - | 取りうる値が限られるときは列挙し、各値の意味は補足に書く。 | - |
| endpoints[].request[].required | 必須 | boolean | - | - | - | - | - |
| endpoints[].request[].default | 既定 | string | - | - | - | 任意のパラメータの省略時の値。 | - |
| endpoints[].request[].description | 説明 | string | 必須 | - | - | - | - |
| endpoints[].request[].constraints | 制限 | string | - | - | - | - | - |
| endpoints[].request[].notes | 補足 | string | - | - | - | - | - |
| endpoints[].request[].location | 置き場所 | string | - | path / query / header / cookie / body | - | - | - |
| endpoints[].request[].format | 形式 | string | - | - | - | - | - |
| endpoints[].request[].example | 例 | string | - | - | - | - | - |
| endpoints[].request[].nullable | 空を許す | boolean | - | - | - | - | - |
| endpoints[].request[].status | 状態 | string | - | planned / implemented / deprecated / removed | - | 項目の状態。`planned`（予定）/ `implemented`（実装済み）/ `deprecated`（非推奨）/ `removed`（廃止）。書かなければ実装済みとして扱う。 | - |
| endpoints[].request_example | リクエスト例 | string | - | - | - | JSON のコードブロック。body を持たないときはリクエストライン。 | - |
| endpoints[].response | レスポンス | array | - | - | - | 別のエンドポイントと同形のときは持たず、`same_as` に書く。 | - |
| endpoints[].response[].name | フィールド | string | 必須 | - | - | 返らないことがあるフィールドは `field?` と書き、条件を補足に書く。 | - |
| endpoints[].response[].type | 型 | string | 必須 | - | - | - | - |
| endpoints[].response[].description | 説明 | string | 必須 | - | - | - | - |
| endpoints[].response[].constraints | 制限 | string | - | - | - | - | - |
| endpoints[].response[].notes | 補足 | string | - | - | - | - | - |
| endpoints[].same_as | 同形のレスポンス | string | - | - | - | レスポンスが同形のエンドポイントの名前。 | - |
| endpoints[].response_headers | 応答のヘッダー | array | - | - | - | - | - |
| endpoints[].response_headers[].name | ヘッダー | string | 必須 | - | - | - | - |
| endpoints[].response_headers[].description | 説明 | string | 必須 | - | - | - | - |
| endpoints[].response_headers[].notes | 補足 | string | - | - | - | - | - |
| endpoints[].response_example | レスポンス例 | string | - | - | - | JSON のコードブロック。 | - |
| endpoints[].status_codes | ステータスコード | array | 必須 | - | minItems: 1 | 正常・異常とも網羅する。 | - |
| endpoints[].status_codes[].code | ステータスコード | string | 必須 | - | - | - | - |
| endpoints[].status_codes[].condition | 発生条件 | string | 必須 | - | - | - | - |
| endpoints[].status_codes[].notes | 補足 | string | - | - | - | 再試行の方針など。 | - |
| endpoints[].refs | 関連 | array | - | - | - | - | - |
| endpoints[].reason | 理由 | string | - | - | - | そうしている理由。読み手の判断が変わるものだけを書く。 | - |
| endpoints[].status | 状態 | string | - | planned / implemented / deprecated / removed | - | 項目の状態。`planned`（予定）/ `implemented`（実装済み）/ `deprecated`（非推奨）/ `removed`（廃止）。書かなければ実装済みとして扱う。 | - |
| endpoints[].visibility | 公開 | string | - | user / developer | - | 公開の範囲。`user`（ユーザー向け）/ `developer`（開発者向け）。<br>書かなければ親の値を引き継ぎ、最上位の既定は `developer`。 | - |
| endpoints[].implementation | 実装 | string | - | - | pattern: ^[^#\s]+(#\S+)?$ | 実装の場所。リポジトリの直下からのファイルのパスに、`#` とシンボルの名前を続けてよい。 | `src/app/features/profile/service.py#update_profile` |
| endpoints[].introduced | 導入 | object | - | - | - | 入ったバージョンと PR。 | - |
| endpoints[].introduced.version | バージョン | string | - | - | - | 入ったバージョンのタグ（例 `v0.3.0`）。 | - |
| endpoints[].introduced.pr | PR | integer | - | - | - | 入れた PR の番号。 | - |
| endpoints[].aliases | 別名 | array | - | - | - | 検索で当てたい言い換え。 | - |
| endpoints[].notes | 補足 | object | - | - | - | 項目に分けられない残り。セクションの名前 → 本文。<br>同じ名前のセクションが多くの設計書に出たら、標準の項目へ格上げする候補になる。 | - |
| issues | 不具合一覧 | array | - | - | - | 仕様どおりに使っても期待どおり動かない事象。こちらの使い方の誤りだったものは書かない。解消を確かめたら削除する。 | - |
| issues[].title | タイトル | string | 必須 | - | - | - | - |
| issues[].summary | 概要 | string | 必須 | - | minLength: 1, pattern: ^[^\n]+$ | 1 行で事象を要約する。 | - |
| issues[].occurred_on | 発生日 | string | 必須 | - | pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ | 事象を確認した日（`YYYY-MM-DD`）。再確認して続いていたら更新する。 | - |
| issues[].state | 状態 | string | - | 未解決 / 回避策あり / 解消済み | - | - | - |
| issues[].description | 概要 | string | 必須 | - | - | 何が起きるかを事実だけで書く。 | - |
| issues[].conditions | 条件 | array | - | - | - | 再現する状況。 | - |
| issues[].workarounds | 対処法 | array | 必須 | - | minItems: 1 | - | - |
| issues[].workarounds[].method | 方法 | string | 必須 | - | - | 回避策が無いときは `回避策なし`。 | - |
| issues[].workarounds[].result | 結果 | string | 必須 | - | - | 得られるものと、本来やりたかったことからのずれ。 | - |
| issues[].workarounds[].recommended | 推奨 | boolean | - | - | - | 最初に試す 1 案だけ。 | - |
| issues[].upstream_issue | 上流の Issue | string | - | - | - | 上流の Issue の URL。 | - |
| issues[].fixed_in | 解消バージョン | string | - | - | - | 解消したバージョン。達したら回避策を外す候補になる。 | - |
| issues[].refs | 関連 | array | - | - | - | - | - |
| issues[].notes | 補足 | object | - | - | - | 項目に分けられない残り。セクションの名前 → 本文。<br>同じ名前のセクションが多くの設計書に出たら、標準の項目へ格上げする候補になる。 | - |
| refs | 関連 | array | - | - | - | - | - |
| notes | 補足 | object | - | - | - | 項目に分けられない残り。セクションの名前 → 本文。<br>同じ名前のセクションが多くの設計書に出たら、標準の項目へ格上げする候補になる。 | - |

<!-- /table -->

## 記載例

```yaml
title: OpenAI
lead: OpenAI が提供する LLM・埋め込み・音声の API。
used_in:
- integrations/openai/
verification:
  state: 済
  date: '2026-01-10'
  detail: チャットの応答を 1 回取得した
version:
  api_version: v1（URL 埋め込み型）
  checked_on: '2026-07-24'
base_urls:
- env: 本番
  url: https://api.openai.com/v1
official_url: https://openai.com/api/
docs_url: https://platform.openai.com/docs/api-reference
auth:
  method: Bearer トークン（API キー）
  steps: |-
    1. https://platform.openai.com/api-keys を開く
    2. `Create new secret key` で API キーを作る
    3. 作ったキーを控える（再表示できない）
  env_vars:
  - OPENAI_API_KEY
rate_limits:
- target: gpt-4o-mini
  limit: 500 RPM / 200,000 TPM
  notes: tier 1
retry: 超過すると 429 を返す。Exponential Backoff（1 秒 → 2 秒 → 4 秒）で最大 3 回再試行する。
pricing:
- target: gpt-4o-mini
  price: 入力 $0.150 / 出力 $0.600（1M トークン）
pricing_url: https://openai.com/api/pricing/
endpoints:
- name: POST /chat/completions
  method: POST
  path: /chat/completions
  summary: チャット形式の LLM の応答を作る
  request:
  - name: model
    type: string
    required: true
    location: body
    description: モデル名
  - name: messages
    type: '{ role, content }[]'
    required: true
    location: body
    description: チャットの履歴
  - name: messages[].role
    type: '"system" or "user" or "assistant"'
    required: true
    location: body
    description: 送信者の役割
  - name: temperature
    type: number
    required: false
    default: '1'
    location: body
    description: 応答のばらつき
    constraints: 0〜2
  request_example: |-
    ```json
    {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}]}
    ```
  response:
  - name: choices[].message.content
    type: string
    description: 生成されたテキスト
  - name: usage.prompt_tokens
    type: number
    description: 入力のトークン数
  status_codes:
  - code: '200'
    condition: 正常
  - code: '401'
    condition: API キーが不正
  - code: '429'
    condition: レートリミットの超過
    notes: Exponential Backoff で最大 3 回再試行する
```
