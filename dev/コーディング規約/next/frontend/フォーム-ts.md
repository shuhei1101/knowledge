# {feature}/form.ts — Zod schema + Type

- 配置: フィーチャ直下（new / edit 共用）
- `defaultXxxForm` を export（new 画面で使用）
- エラーメッセージは日本語
- 共通プリミティブ（`IdSchema` / `IconIdSchema` 等）は `app/(shared)/schema.ts` に集約
- route.ts / actions.ts で同じ schema を別定義しない（form.ts を共用）
