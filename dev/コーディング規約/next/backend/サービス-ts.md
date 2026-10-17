# app/api/v{N}/{resource}/service.ts

ビジネスロジック層。**トランザクション境界** を持ち、複数の `query.ts` / `db.ts` 関数を組み合わせて 1 つの業務ユニットを実行する。

## ルール

- `db.transaction(async (tx) => { ... })` でラップ（トランザクション境界）
- 中の関数（`insertXxx` 等）には `tx` を渡す（呼び出し元がトランザクションを決める）
- `AppError` 派生（`ClientValueError`, `ClientAuthError`, `VersionConflictError` 等）はそのまま投げる
- それ以外を `DatabaseError` でラップして再投
- 削除時は `recordHistory` で履歴退避 → `deleteXxx` ハードデリート の順（`DB変更履歴.md` 参照）
- 楽観的ロックの `updatedAt` は呼び出し側から受け取り `updateXxx` に渡す（`DB楽観的ロック.md`）
- 監査が必要なテーブルでは `createdBy` / `updatedBy` を record に含める

## トランザクションの書き方

- 例外を投げればロールバック（自動）
- `await db.transaction(...)` は try の外に書き、catch で `AppError` はそのまま再 throw、それ以外を `DatabaseError` でラップ

```ts
export const registerResource = async ({ db, userId, form }) => {
  return await db.transaction(async (tx) => {
    const { id } = await insertResource({ db: tx, record: ... })
    await insertResourceTags({ db: tx, resourceId: id, tags: form.tags })
    return { id }
  })
}
```

## 命名

- 動詞 + 名詞（`registerResource`, `editResource`, `removeResource`, `activatePublicQuest`）
- HTTP メソッドと 1:1 ではない（業務ユニット名で命名）
