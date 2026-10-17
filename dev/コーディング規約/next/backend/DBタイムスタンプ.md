# drizzle/schema.ts — 共通カラム（timestamps / auditFields）

- 全テーブル共通の `createdAt` / `updatedAt` と、機密データ向けの `createdBy` / `updatedBy`。
- ISO 8601 文字列として扱うと
  - JSON シリアライズで Date オブジェクトの問題がない
  - Server Component → Client Component の props 渡しが安全
  - TanStack Query のキャッシュ等で扱いやすい

```ts
// drizzle/_helpers.ts（または schema.ts 冒頭）
import { timestamp, uuid, text } from "drizzle-orm/pg-core"

/** 作成/更新日時 — 全テーブル共通 */
export const timestamps = {
  /** 作成日時 */
  createdAt: timestamp("created_at", { withTimezone: true, mode: "string" })
    .notNull()
    .defaultNow(),
  /** 更新日時 */
  updatedAt: timestamp("updated_at", { withTimezone: true, mode: "string" })
    .notNull()
    .defaultNow(),
}

/** 監査カラム — 機密データテーブルに付与 */
export const auditFields = {
  /** 作成者 user ID */
  createdBy: text("created_by"),    // user.id が text 型なので text
  /** 最終更新者 user ID */
  updatedBy: text("updated_by"),
}
```

使用時:
```ts
// マスター系 — timestamps なしで OK（不変なら）
export const icons = pgTable("icons", {
  id: integer("id").primaryKey().generatedAlwaysAsIdentity(),
  name: text("name").notNull().unique(),
})

// データ系 — timestamps 必須
export const resources = pgTable("resources", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  ...timestamps,
})

// 機密データ系 — auditFields も付与
export const orders = pgTable("orders", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  amount: integer("amount").notNull(),
  ...timestamps,
  ...auditFields,
})
```


updatedAtは アプリケーション側で明示更新する:
  - トリガーで自動更新すると `RETURNING` の値が古い updatedAt のままなど、楽観ロックで問題になることがある。
```ts
// db.ts
await db.update(resources)
  .set({ ...record, updatedAt: new Date().toISOString() })
  .where(...)
```
