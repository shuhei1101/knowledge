# use{Feature}UrlState.ts — URL クエリ state hook

- nuqs 推奨
- `app/layout.tsx` に `<NuqsAdapter>` が必要
- 配置: `{feature}/hooks/use{Feature}UrlState.ts`

## ルール

- フィルタ / ソート変更時は ページ 1 にリセット必須
- nuqs の `history` は既定が `replace`。フィルタ / ソート変更は `history: "push"` を指定する。debounced search 等は `replace` のまま
- URL に出す: タブ / フィルタ / ソート / ページ / 選択中 ID
- URL に出さない: PII / フォーム入力中の値 / Loading or Error UI
