# Server Action をクライアントから呼ぶ — useTransition / useActionState / useFormStatus

- mutation の第一選択は Server Action 直接呼び。単純なフォームは `useTransition` + 自前ハンドラ
- 失敗 / 成功は 必ず通知（失敗は toast or フィールドエラー）

| ケース                             | 推奨                                    |
| ---------------------------------- | --------------------------------------- |
| フォーム送信（リッチ UI）          | `useTransition` + 自前ハンドラ          |
| プログレッシブエンハンスメント必要 | `useActionState` + `<form action>`      |
| `<form>` 内のサブミットボタン      | `useFormStatus`                         |
| 楽観 UI                            | `useOptimistic` (+ useTransition)       |
| 複雑な楽観更新 / キャンセル        | useMutation（`useMutationパターン.md`） |
