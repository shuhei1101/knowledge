# app/api/v{N}/{resource}/db.ts

- 書き込み（INSERT / UPDATE / DELETE）専用ファイル。`service.ts` から呼ばれる。
- 1 関数 = 1 SQL 文（複数文の組み合わせは `service.ts` で）
- 引数は オブジェクト で受ける（`{ db, id, record }`）
- `db` 引数は `Db` 型（`tx` も同じ型なのでトランザクション内でも使える）
- 失敗は 必ず `DatabaseError` で包む（生の Drizzle error を投げない）
- update の楽観的ロック実装は `DB楽観的ロック.md`
- 戻り値:
  - `insertXxx` → `returning()` で row を返す
  - `updateXxx` → `returning()` で row を返す（呼び出し側が利用）
  - `deleteXxx` → void

## 必須テンプレ

```ts
import { eq, and } from "drizzle-orm"
import type { Db } from "@/drizzle/db"
import { resources, type ResourceInsert, type ResourceUpdate } from "@/drizzle/schema"
import { DatabaseError, VersionConflictError } from "@/app/(shared)/errors/appError"

/** リソースを挿入 */
export const insertResource = async ({ db, record }: { db: Db; record: ResourceInsert }) => {
  try {
    const [row] = await db.insert(resources).values(record).returning()
    return row
  } catch (e) {
    throw new DatabaseError("リソースの登録に失敗しました。", { cause: e })
  }
}

/** リソースを削除（ハードデリート） */
export const deleteResource = async ({ db, id }: { db: Db; id: string }) => {
  try {
    await db.delete(resources).where(eq(resources.id, id))
  } catch (e) {
    throw new DatabaseError("リソースの削除に失敗しました。", { cause: e })
  }
}
```

## 命名

- `insert{Feature}` — INSERT
- `update{Feature}` — UPDATE
- `delete{Feature}` — DELETE
- `upsert{Feature}` — INSERT ON CONFLICT
- `insert{Feature}Tags` — 関連テーブル操作

## バルク操作

```ts
export const insertResourceTags = async ({ db, resourceId, tags }: {
  db: Db
  resourceId: string
  tags: { name: string }[]
}) => {
  try {
    const records = tags.map((t) => ({ resourceId, name: t.name }))
    await db.insert(resourceTags).values(records)
  } catch (e) {
    throw new DatabaseError("タグの登録に失敗しました。", { cause: e })
  }
}

export const deleteResourceTags = async ({ db, resourceId }: { db: Db; resourceId: string }) => {
  try {
    await db.delete(resourceTags).where(eq(resourceTags.resourceId, resourceId))
  } catch (e) {
    throw new DatabaseError("タグの削除に失敗しました。", { cause: e })
  }
}
```
