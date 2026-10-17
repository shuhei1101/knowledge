# {Feature}EditScreen.tsx / {Feature}NewScreen.tsx

shadcn `<Form>` + react-hook-form + Zod + Server Action。

- `'use client'` 必須
- `useTransition` で `isPending` 管理
- `defaultValues` に Server から受け取った値を流す
- mutation は Server Action（`useMutation` ではない）

## 送信フロー

1. `form.handleSubmit(onSubmit)` → `startTransition(async () => { ... })`
2. Server Action の戻り値 `result.ok` を判定
3. 失敗: `error.field` があれば `form.setError`、なければ `toast.error`
4. 成功（edit）: `toast.success` + `form.reset(data)`
5. 成功（new）: `toast.success` + `router.push(RESOURCE_URL.view(id))`

## ルール

- dirty 判定は `formState.isDirty`（`JSON.stringify` 比較しない）
- 保存ボタンは `disabled={!form.formState.isDirty || isPending}`
