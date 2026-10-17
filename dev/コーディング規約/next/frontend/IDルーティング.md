# [id]/ — レコード単位のルーティング

- `[id]/page.tsx` が View 画面そのもの、編集は `[id]/edit/page.tsx`
- view/edit 共通の hook / components は `[id]/` 直下、Edit 専用は `[id]/edit/` 配下
- View 専用フィールド（`viewCount` 等）が要るときだけ View 専用フックを別途作る（共通に混ぜない）

## 構成

```
app/(authenticated)/{feature}/[id]/
├── page.tsx                       # View (Server Component)
├── {Feature}ViewScreen.tsx        # View (Client Component)
├── components/                    # view/edit 共通
│   └── {Feature}Header.tsx
├── hooks/                         # view/edit 共通
│   └── use{Feature}.ts
└── edit/
    ├── page.tsx
    ├── {Feature}EditScreen.tsx
    ├── components/                # edit 専用
    └── hooks/
        └── use{Feature}Form.ts
```

## 権限ガード

編集権限なしで `/edit` 直アクセスされた場合:
- 推奨: Edit の page.tsx で `fetchResource` の `canEdit` を見て `redirect(RESOURCE_URL.view(id))`（取得結果を再利用できる）
- 軽量チェックなら proxy.ts でブロック（`backend/プロキシ.md`）

## View がない画面

設定画面など Edit のみのフィーチャは `settings/page.tsx` に直接 EditScreen を render する（`[id]/` パターンに無理に当てはめない）。
