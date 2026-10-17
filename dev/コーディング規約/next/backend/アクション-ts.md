# app/(authenticated)/{feature}/actions.ts

- Server Action 群。mutation の第一選択。
  - ファイル冒頭に `'use server'` を置けば、export された全関数が Server Action になる。
- ファイル先頭に `'use server'`
- 戻り値は `ActionResult<T>` 形式に統一
- 入力は 必ず Zod で `.parse`（クライアント信用しない）
- 認証は `getAuthContext()`（呼ばないとセキュリティ違反）
- 業務処理は `service.ts` 経由（DB 操作を直接書かない）
- `revalidateTag` は 第 2 引数の cacheLife プロファイル必須（Next.js 16）
- 必要なら `refresh()` で client router を更新

## ファイル配置
s
- `app/(authenticated)/{feature}/actions.ts` — フィーチャ固有
- `app/(shared)/actions/{name}.ts` — 複数フィーチャ共通（auth 等）

## 命名

- `{verb}{Feature}Action` プレフィックス（`registerResourceAction`, `updateResourceAction`, `deleteResourceAction`）
- 動詞は `register` / `update` / `delete` / `activate` / `archive` / `publish` 等
