# app/(authenticated)/{feature}/actions.ts

- Server Action 群。mutation の第一選択。
- ファイル先頭に `'use server'`
- 戻り値は `ActionResult<T>` 形式に統一
- 入力は 必ず Zod で `.parse`（クライアント信用しない）
- 認証は `getAuthContext()`（呼ばないとセキュリティ違反）。対象リソースへの権限（所有者・ロール）も確認する
- 業務処理は `service.ts` 経由（DB 操作を直接書かない）
- 戻り値には UI が使う項目だけを入れる（DB の行をそのまま返さない）
- キャッシュの無効化と `refresh()` は `キャッシュ.md` に従う

## ファイル配置

- `app/(authenticated)/{feature}/actions.ts` — フィーチャ固有
- `app/(shared)/actions/{name}.ts` — 複数フィーチャ共通（auth 等）

## 命名

- `{verb}{Feature}Action` プレフィックス（`registerResourceAction`, `updateResourceAction`, `deleteResourceAction`）
- 動詞は `register` / `update` / `delete` / `activate` / `archive` / `publish` 等
