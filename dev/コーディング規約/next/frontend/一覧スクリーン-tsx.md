# {Feature}ListScreen.tsx — 一覧 Client Component

- `'use client'` 必須
- Server から `initial` データを受け取る（クライアント初回 fetch は FOUC が出るので禁止）
- URL state hook と data hook を並列呼び
- フィルタ / ソート / ページは `useState` 禁止 → URL state

## 必須要素

- `<ScreenWrapper>` で外殻
- `<PageHeader>` でタイトル
- フィルタ / ソート UI
- loading: `<Skeleton>`
- 空: `<EmptyState>`（必須、白画面禁止）
- `<Pagination>`

## hook の依存

- `use{Feature}UrlState` — URL state（`frontend/useUrlStateパターン.md`）
- `use{Feature}s` — TanStack Query（`frontend/useQueryパターン.md`）
