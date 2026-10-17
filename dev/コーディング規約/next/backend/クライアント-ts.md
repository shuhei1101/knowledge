# app/api/v{N}/{resource}/client.ts

クライアント側 fetch ヘルパー。フロントエンドの hook / Server Component から呼ぶ。

## ルール

- リクエスト型は `route.ts` から `import type`（重複定義禁止）
- フィルタ型・戻り値型は `query.ts` から `import type`
- URL は `app/(shared)/endpoints.ts` の定数経由（ハードコード禁止）
- 非 OK レスポンスは `AppError.fromResponse(json, status)` で投げる
- 戻り値は 封筒の `data` を unwrap して返す（呼び出し側で `.data` を書かなくていい）
- `JSON.stringify(req)` で送る前に Zod パースする必要はない（route.ts 側が parse する）

## 命名

- `getXxx` — 単体取得
- `getXxxs` / `getXxxList` — 一覧
- `postXxx` — 作成
- `patchXxx` — 部分更新
- `putXxx` — 全置換（使う場合）
- `deleteXxx` — 削除
