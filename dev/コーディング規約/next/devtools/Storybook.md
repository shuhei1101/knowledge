# Next.js App Router — Storybook

> **目的**: shadcn/ui 拡張コンポーネントのカタログを可視化し、デザイン確認・テスト・ドキュメント化を一元化。
> **Stack**: Storybook + `@storybook/nextjs-vite` + Vitest 統合（版は [Storybook のドキュメント](https://storybook.js.org/docs)）。

- 共通コンポーネント（`app/(shared)/components/`）の `.stories.tsx` を 同じディレクトリ に置く
- フィーチャ固有のコンポーネントは story 不要（E2E でカバー）
- 状態のあるコンポーネント（Dialog 等）は `play` 関数で操作
- `next/navigation` を使うコンポーネントは `parameters.nextjs.appDirectory: true` を付ける

`addon-a11y` を入れると、各 Story で axe-core によるチェックが走り、違反が UI に表示される。
`addon-themes` で全 Story にテーマ切替トグルを追加する。
`@chromatic-com/storybook` で各 Story を Chromatic にアップし、視覚回帰テストにする。

| Category      | 用途                                                       |
| ------------- | ---------------------------------------------------------- |
| `Shared`      | `app/(shared)/components/` のカスタム                      |
| `Shared / UI` | `app/(shared)/components/ui/` の shadcn コピー（必要なら） |
| `Patterns`    | パターン例（List 画面風、Edit 画面風）                     |
| `Forms`       | フォーム例                                                 |
| `Pages`       | ページ全体のスタブ（任意）                                 |
