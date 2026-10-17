# Drizzle — 楽観的ロック

- `updatedAt` 比較で「他のユーザーによる先行更新」を検知する標準パターン。
  - 全 update に `updatedAt` 比較必須（楽観ロックなしの update 禁止）
  - `WHERE id = ? AND updatedAt = ?` の 両方一致 が条件
- 一致しない（`returning()` が空）→ `VersionConflictError` を投げる
- 更新時に `updatedAt` を 新しい時刻に書き換える（次の更新の基準に）
- `mode: "string"` で持っているので ISO 文字列比較になる

```ts
import { and, eq } from "drizzle-orm"
import { VersionConflictError, DatabaseError } from "@/app/(shared)/errors/appError"

export const updateResource = async ({ db, id, updatedAt, record }: {
  db: Db
  id: string
  updatedAt: string      // クライアントから受け取った「最後に見た」timestamp
  record: ResourceUpdate
}) => {
  try {
    const [row] = await db.update(resources)
      .set({ ...record, updatedAt: new Date().toISOString() })
      .where(and(eq(resources.id, id), eq(resources.updatedAt, updatedAt)))
      .returning()

    if (!row) throw new VersionConflictError("他のユーザーによって更新されています。")
    return row
  } catch (e) {
    if (e instanceof VersionConflictError) throw e
    throw new DatabaseError("リソースの更新に失敗しました。", { cause: e })
  }
}
```

`updatedAt` ナノ秒精度の問題が懸念される場合、`version: integer` 列を併用:

```ts
export const resources = pgTable("resources", {
  // ...
  /** バージョン — 楽観的ロック用 */
  version: integer("version").notNull().default(1),
  ...timestamps,
})
```


外部公開 API では `ETag` ヘッダ + `If-Match` で:

```ts
// GET response
res.headers.set("ETag", `"${row.updatedAt}"`)

// PATCH 時にクライアントが If-Match: "..." を送る
const ifMatch = request.headers.get("if-match")
// ifMatch を updatedAt として update に渡す
```

internal API では `updatedAt` を JSON body に含めて送る方が簡単。
