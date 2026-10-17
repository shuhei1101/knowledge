# app/api/v{N}/{resource}/dbHelper.ts

- リソース内で複数の `query.ts` / `db.ts` 関数から共通利用するヘルパー。
- リソース内に閉じる共通処理だけを置く
- 複数リソース横断で使うものは `app/(shared)/lib/` に格上げ（`app/(shared)/lib/pagination.ts` 等）
- 純粋関数を優先（テストしやすい）
- DB 接続を取らない（受け取る側で扱う）

## テンプレ

```ts
/** ページング計算 */
export const calculatePagination = ({ page, pageSize }: { page: number; pageSize: number }) => ({
  offset: (page - 1) * pageSize,
  limit: pageSize,
})

/** リソース全体に共通する WHERE 条件 */
export const buildResourceVisibilityCondition = (userId: string) => {
  // 例: 公開フラグ or 自分のリソース
  return or(eq(resources.isPublic, true), eq(resources.createdBy, userId))
}
```
