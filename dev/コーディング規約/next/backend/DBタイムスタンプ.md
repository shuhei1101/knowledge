# drizzle/schema.ts — 共通カラム（timestamps / auditFields）

- 全テーブル共通の `createdAt` / `updatedAt` と、機密データ向けの `createdBy` / `updatedBy`。
- `timestamp` は `mode: "string"` で持つ。値は DB サーバーのタイムゾーンの Postgres 形式の文字列で返り、`toISOString()` の形式とは限らない

```ts
// drizzle/_helpers.ts（または schema.ts 冒頭）
import { timestamp, text } from "drizzle-orm/pg-core"

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
- マスター系 — 不変なら `timestamps` なしで OK
- データ系 — `...timestamps` 必須
- 機密データ系 — `...timestamps` に加えて `...auditFields` も付与

`updatedAt` はアプリケーション側で明示更新する（書き方は `DB楽観的ロック.md`）。
