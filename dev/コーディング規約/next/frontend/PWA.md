# PWA / Offline

## manifest

- `app/manifest.ts` で `MetadataRoute.Manifest` を返す（`<link rel="manifest">` は Next.js が自動付与）
- 必須項目: name / short_name / start_url / scope / `display: "standalone"` / theme_color / icons（192・512・maskable の 3 種）

## Apple 対応

- `app/layout.tsx` の `metadata.appleWebApp`（capable / statusBarStyle / title）
- `apple-touch-icon.png` を `app/` 直下か `public/` に

## Service Worker

Next.js は SW を直接サポートしないので `@serwist/next` を使う:
- next.config.ts を `withSerwistInit({ swSrc: "app/sw.ts", swDest: "public/sw.js" })` で wrap
- `app/sw.ts` で `new Serwist({ precacheEntries: self.__SW_MANIFEST, skipWaiting: true, clientsClaim: true, runtimeCaching: defaultCache })` + `addEventListeners()`
- 動作確認は DevTools の Application タブ
