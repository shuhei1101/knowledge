# useMutation パターン

第一選択は Server Action 直接呼び（`useTransition` + `actions.ts`）。
以下が必要なときのみ `useMutation` を使う:
- 楽観更新
- mutation のキャンセル
- 並列 mutation 管理
- 細かいリトライ / バックオフ

## 楽観更新の許可リスト

✅ いいね / お気に入り / ブックマーク / フォロー / リアクション / トグル状態  
❌ 課金 / フォーム保存 / 重要なデータ作成・削除

## 楽観更新パターン

`onMutate`: 競合 query キャンセル → snapshot 退避 → 楽観更新  
`onError`: snapshot でロールバック  
`onSettled`: `invalidateQueries`

## 命名

`use{Verb}{Feature}` — `useToggleResourceFavorite`, `useArchiveResource`
