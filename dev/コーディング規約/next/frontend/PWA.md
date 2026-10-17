# PWA / Offline

## manifest

- `app/manifest.ts` で `MetadataRoute.Manifest` を返す
- 必須項目: name / short_name / start_url / scope / `display: "standalone"` / theme_color / icons（192・512・maskable の 3 種）

## Apple 対応

- `app/layout.tsx` の `metadata.appleWebApp`（capable / statusBarStyle / title）
- `apple-touch-icon.png` を `app/` 直下か `public/` に

## Service Worker

Next.js は SW を直接サポートしないので Serwist を使う。Next.js 16 の既定の bundler は Turbopack のため `@serwist/turbopack` を使う（`@serwist/next` は webpack 用）。導入手順は [Serwist の Turbopack ガイド](https://serwist.pages.dev/docs/next/turbo)。
