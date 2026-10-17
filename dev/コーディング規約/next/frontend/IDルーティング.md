# [id]/ — レコード単位のルーティング

- `[id]/page.tsx` が View 画面そのもの、編集は `[id]/edit/page.tsx`
- フォルダ構成は `frontend/フィーチャーフォルダ.md`
- View 専用フィールド（`viewCount` 等）が要るときだけ View 専用フックを別途作る（共通に混ぜない）

## 権限ガード

編集権限なしで `/edit` 直アクセスされた場合:
- 推奨: Edit の page.tsx で `fetchResource` の `canEdit` を見て `redirect(RESOURCE_URL.view(id))`
- 軽量チェックなら proxy.ts でブロック（`backend/プロキシ.md`）

## View がない画面

設定画面など Edit のみのフィーチャは `settings/page.tsx` に直接 EditScreen を render する（`[id]/` パターンに無理に当てはめない）。
