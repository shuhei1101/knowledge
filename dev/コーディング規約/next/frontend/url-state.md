# URL-Based Screen State — 原則

ユーザーが画面で見ているものに影響する state（タブ・フィルタ・ソート・ページ・選択中 ID）は URL クエリに置く。シェア可能・戻る / 進むが正しく動く・リフレッシュ復元・deep link が機能する。

URL に置く / 置かないの基準と hook 実装（nuqs / 自前）は `frontend/useUrlStateパターン.md`。

## 読み取り

- Server Component: `const sp = await props.searchParams`
- Client Component: `useSearchParams()`
- 配列は `searchParams.getAll("tag")`

## 書き込み

- `URLSearchParams` を組み立てて `router.push(`${pathname}?${params}`)`
- `null` / 空文字はキーを delete、配列は delete してから append
- Screen は hook 経由でアクセスし `useRouter` を直接触らない

## バリデーション

URL クエリは外部入力なので Zod で parse し、不正な値は既定値に落とす。

## Tab 連携

shadcn `<Tabs>` の `value` / `onValueChange` に URL state を渡す。
