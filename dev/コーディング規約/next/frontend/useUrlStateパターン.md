# use{Feature}UrlState.ts — URL クエリ state hook

- nuqs 推奨（`parseAsString` / `parseAsInteger` / `parseAsArrayOf` / `parseAsStringEnum`）
- `app/layout.tsx` に `<NuqsAdapter>` が必要
- 配置: `{feature}/hooks/use{Feature}UrlState.ts`

## ルール

- フィルタ / ソート変更時は ページ 1 にリセット必須
- `router.push` がデフォルト（history 残す）。debounced search 等は `router.replace`
- URL に出す: タブ / フィルタ / ソート / ページ / 選択中 ID
- URL に出さない: PII / フォーム入力中の値 / Loading or Error UI
