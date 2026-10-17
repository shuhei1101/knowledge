# {feature}/[id]/edit/page.tsx — Edit Server Component

- 該当なし → `notFound()`
- 権限なし → `redirect(RESOURCE_URL.view(id))`（URL クエリからリダイレクト先取得禁止）
- `canEdit` は `fetchResource` のレスポンスに含まれる

## new 用

`new/page.tsx` はデータ取得なし（空フォームから始まる）。
