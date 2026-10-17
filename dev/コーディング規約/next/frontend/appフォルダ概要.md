# app/ — フォルダ全体図

Next.js App Router プロジェクトの `app/` 配下の構成。モノレポ前提で通常は `packages/web/app/`。
- モノレポ前提（`packages/web/` 配下）
- Route Group は `(authenticated)` `(auth)` `(shared)` の 3 つに統一
- API ルートは `/api/v{N}/` 配下（バージョニング）
- `proxy.ts` はプロジェクト直下（Next.js 16 で `middleware.ts` から rename）
- 共通要素は `app/(shared)/` 配下

## トップレベル

```
packages/web/app/
├── (authenticated)/   # 認証必須エリア — メイン画面群
├── (auth)/            # 認証画面（login / signup / reset-password）
├── (shared)/          # 共通コンポーネント・hook・provider・schema
├── api/v{N}/            # バージョニング済み API ルート
├── error/             # エラーページ（unauthorized 等）
├── layout.tsx         # ルートレイアウト
├── error.tsx          # ルートエラーバウンダリ
├── global-error.tsx   # ルート layout 自体のエラー
├── not-found.tsx      # 404
└── loading.tsx        # ルート suspense fallback
```

プロジェクト直下:

```
packages/web/
├── proxy.ts           # Next.js 16: 旧 middleware.ts
├── drizzle/           # DB スキーマ
├── tests/             # E2E / Unit テスト
├── config/
│   └── settings.yaml  # YAML 構造化設定
└── stories/           # Storybook 用（任意）
```

## page.tsx 共通原則

- `page.tsx` は async Server Component（`'use client'` / `useState` / `useQuery` を付けない）
- データ取得は `query.ts` の `fetchXxx` を直接 import（自分の API へ `fetch(/api/...)` しない）
- 取得データは Client Screen に props で渡す
