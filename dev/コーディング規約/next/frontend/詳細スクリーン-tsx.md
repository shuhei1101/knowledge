# {Feature}ViewScreen.tsx — View Client Component

- `'use client'` 必須
- Server Component から `resource` props を受け取る（fetch しない）
- 読み取り専用（`useMutation` / `<form>` なし）
- `resource.canEdit` で編集ボタン出し分け
- 編集遷移は `RESOURCE_URL.edit(id)` で URL 定数経由

## TanStack Query との連携

view/edit 共通の hook がある場合は `initialData` に props を渡して hydrate:

```ts
const { data } = useResource({ resourceId, initialData: resource })
```
