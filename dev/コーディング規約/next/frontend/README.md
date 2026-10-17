# frontend

next/frontend の規約

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [404-tsx](./404-tsx.md) | `notFound()` が呼ばれた時に表示される Server Component。 |
| [IDルーティング](./IDルーティング.md) | 詳細画面と編集画面の `[id]` のルーティング |
| [PWA](./PWA.md) | PWA / Offline |
| [SEO](./SEO.md) | Next.js App Router — SEO / Metadata |
| [Zustandパターン](./Zustandパターン.md) | Context で足りないときの Zustand の使い方 |
| [appフォルダ概要](./appフォルダ概要.md) | Next.js App Router プロジェクトの `app/` 配下の構成。モノレポ前提で通常は `packages/web/app/`。 |
| [url-state](./url-state.md) | ユーザーが画面で見ているものに影響する state（タブ・フィルタ・ソート・ページ・選択中 ID）は URL クエリに置く。シェア可能・戻る / 進むが正しく動く・リフレッシュ復元・deep link が機能する。 |
| [useActionState](./useActionState.md) | mutation を Server Action で行うときのフォームの書き方 |
| [useFormパターン](./useFormパターン.md) | フォームの hook の書き方 |
| [useMutationパターン](./useMutationパターン.md) | 第一選択は Server Action 直接呼び（`useTransition` + `actions.ts`）。 |
| [useQueryパターン](./useQueryパターン.md) | 読み取りの hook の書き方 |
| [useUrlStateパターン](./useUrlStateパターン.md) | URL クエリの状態を扱う hook の書き方 |
| [アセット](./アセット.md) | Assets (Image / Font / Static) |
| [エラー-tsx](./エラー-tsx.md) | `error.tsx` の書き方 |
| [エンドポイント](./エンドポイント.md) | URL を集める置き場所 |
| [クエリクライアントセットアップ](./クエリクライアントセットアップ.md) | QueryClient の初期化 |
| [コンテキストパターン](./コンテキストパターン.md) | 複数のルート・コンポーネントで共有する UI state の Context |
| [コンポーネントカタログ](./コンポーネントカタログ.md) | 新しいコンポーネントを作る前に見る一覧 |
| [スクリーンラッパー](./スクリーンラッパー.md) | 全画面の最外殻になるスクリーンラッパー |
| [ストリーミング](./ストリーミング.md) | Streaming / Suspense |
| [タグ入力](./タグ入力.md) | タグ入力のコンポーネント |
| [ダイアログ](./ダイアログ.md) | Dialog / Modal / Popup |
| [フィーチャーフォルダ](./フィーチャーフォルダ.md) | フィーチャフォルダ構成 |
| [フォーム-ts](./フォーム-ts.md) | フォームのスキーマと既定値を置く `form.ts` の書き方 |
| [フォームコンポーネント](./フォームコンポーネント.md) | react-hook-form + Zod + shadcn/ui の標準組み合わせ。 |
| [ページヘッダー](./ページヘッダー.md) | ページヘッダーのコンポーネント |
| [ルートグループ](./ルートグループ.md) | ルートグループの分け方 |
| [ルートファイル規約](./ルートファイル規約.md) | 各 route segment で使う標準ファイル（`page.tsx` 以外）の役割と配置規約。 |
| [ローディングボタン](./ローディングボタン.md) | mutation を伴うボタンのコンポーネント |
| [一覧スクリーン-tsx](./一覧スクリーン-tsx.md) | 一覧画面のスクリーンの書き方 |
| [一覧ページ-tsx](./一覧ページ-tsx.md) | 一覧画面の `page.tsx` の書き方 |
| [命名規約](./命名規約.md) | Next.js App Router — Naming Conventions |
| [型規約](./型規約.md) | 型定義の置き場所と表現 |
| [必須マーク](./必須マーク.md) | フォームの必須マークのコンポーネント |
| [状態管理判断基準](./状態管理判断基準.md) | State の置き場所 |
| [確認ダイアログ](./確認ダイアログ.md) | `window.confirm` の代わりに使う確認ダイアログ |
| [空状態](./空状態.md) | 一覧が空のときの表示 |
| [編集スクリーン-tsx](./編集スクリーン-tsx.md) | shadcn `<Form>` + react-hook-form + Zod + Server Action。 |
| [編集ページ-tsx](./編集ページ-tsx.md) | 編集画面の `page.tsx` の書き方 |
| [自動保存](./自動保存.md) | Autosave パターン |
| [自動保存インジケーター](./自動保存インジケーター.md) | 自動保存の状態を出すインジケーター |
| [詳細スクリーン-tsx](./詳細スクリーン-tsx.md) | 詳細画面のスクリーンの書き方 |
| [詳細ページ-tsx](./詳細ページ-tsx.md) | `[id]/page.tsx` が View 本体（`view/` サブルートは作らない）。 |

<!-- /table -->
