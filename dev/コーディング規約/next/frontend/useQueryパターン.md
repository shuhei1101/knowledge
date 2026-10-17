# useQuery パターン

- 1 hook = 1 ファイル、先頭 `'use client'`
- 戻り値はオブジェクト（タプル禁止）
- `queryKey` に結果を変える全パラメータを含める（filter/sort/page/pageSize 等）
- `initialData` に Server Component 値を流して hydrate
- View / Edit で同じ API なら `[id]/hooks/useResource.ts` に共通化

## queryKey

```ts
queryKey: ["resources", filter, sort, page, pageSize]
```

invalidation は prefix マッチ: `queryClient.invalidateQueries({ queryKey: ["resources"] })`

## 命名

| Pattern | Purpose |
|---|---|
| `use{Feature}` | 単体 |
| `use{Feature}s` / `use{Feature}List` | 一覧 |
| `use{Feature}By{Key}` | キー指定 |
