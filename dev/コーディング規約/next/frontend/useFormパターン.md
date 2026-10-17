# hooks/use{Feature}Form.ts — フォーム state hook

- 配置: `{feature}/[id]/edit/hooks/use{Feature}Form.ts`
- `defaultValues` にサーバー値を流す
- 非同期 fetch 時は `values` プロパティを使う（変更で自動 reset、isDirty も正しく動く）
- hook 化は任意。初期値変換が重い・複数箇所で再利用する場合のみ

## ルール

- Zod schema は `{feature}/form.ts` から import
- 送信成功後は `form.reset(data)` で dirty を落とす
- dirty 判定は `formState.isDirty`（JSON.stringify 比較しない）
- `defaultValues` と `values` を両方使わない
