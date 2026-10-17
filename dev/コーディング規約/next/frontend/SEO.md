# Next.js App Router — SEO / Metadata

> Stack: Next.js 16 Metadata API、`sitemap.ts`、`robots.ts`、`manifest.ts`、構造化データ。
1. title はページ固有、`metadataBase` でルート URL 統一
2. description は 120-160 字 で要点
3. OG image は 1200x630 推奨
4. 動的 OG image は `next/og` で（外部サービス不要）
5. 構造化データは主要な詳細ページに（Article / Product / FAQ 等）
6. 認証画面は `noindex`（誤って公開しない）
7. `metadataBase` を必ず設定（相対 URL → 絶対 URL 解決）
8. multi-locale なら `alternates.languages`
