# app/api/v{N}/{resource}/ — フォルダ構成

`app/api/v{N}/{resource}/` 配下の 6 ファイルの責務分離（CQRS）。

```
app/api/v{N}/{resource}/
├── route.ts        # HTTP ハンドラ
├── client.ts       # クライアント側 fetch ヘルパー
├── service.ts      # ビジネスロジック（トランザクション境界）
├── db.ts           # 書き込み（INSERT / UPDATE / DELETE）
├── query.ts        # 読み取り（SELECT 系全部 + フィルタ Zod + 戻り値型）
└── dbHelper.ts     # 共通ヘルパー（任意）
```

## 呼び出し階層

```
route.ts ─→ service.ts ─→ db.ts / query.ts
client.ts ─→ route.ts（型のみ import）
client.ts ─→ query.ts（フィルタ型のみ import）
```

`route.ts` から `db.ts` / `query.ts` を直接呼ぶのは禁止（必ず `service.ts` 経由）。
例外: 単純な読み取りは `route.ts` から `query.ts` を直接呼んでも OK。

## Server Actions との使い分け

mutation の第一選択は **Server Actions**
`route.ts` は以下の場合に限定:

- 外部公開する（モバイル・外部システム）
- 複雑なクエリ・並列処理・条件付きヘッダ
- ストリーミング、Webhook、SSE
