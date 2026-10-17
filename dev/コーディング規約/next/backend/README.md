# backend

next/backend の規約

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [APIフォルダ概要](./APIフォルダ概要.md) | `app/api/v{N}/{resource}/` 配下の 6 ファイルの責務分離（CQRS）。 |
| [DB Enum](./DB Enum.md) | 固定の値を取るカラムを `pgEnum` で定義する決まり |
| [DB-ID設計](./DB-ID設計.md) | テーブルの ID の決め方 |
| [DB-ts](./DB-ts.md) | 書き込み専用のファイル `db.ts` の書き方 |
| [DBタイムスタンプ](./DBタイムスタンプ.md) | 全テーブル共通の作成・更新の日時と作成者・更新者のカラム |
| [DBヘルパー-ts](./DBヘルパー-ts.md) | リソースの中で共通に使う DB のヘルパー |
| [DBマイグレーション](./DBマイグレーション.md) | `drizzle-kit` を使った schema → SQL migration → DB 適用の流れ。 |
| [DBリレーション](./DBリレーション.md) | 外部キー・relations・index の付け方 |
| [DB変更履歴](./DB変更履歴.md) | 削除前に履歴テーブルへ退避する変更履歴の持ち方 |
| [DB楽観的ロック](./DB楽観的ロック.md) | `updatedAt` の比較で先行更新を検知する楽観的ロック |
| [Drizzleスタイル](./Drizzleスタイル.md) | Drizzle の 2 つの API の使い分け |
| [アクション-ts](./アクション-ts.md) | Server Action 群を置く `actions.ts` の書き方 |
| [ウェブフック](./ウェブフック.md) | Next.js App Router — Webhook Receiver |
| [キャッシュ](./キャッシュ.md) | `cacheComponents: true` を有効化（PPR が標準動作: 静的部分はプリレンダ、`cookies()` / `headers()` / `<Suspense>` 内はリクエスト時レンダ + ストリーム）。 |
| [クエリ-ts](./クエリ-ts.md) | 読み取り（SELECT）専用ファイル。SELECT 関数群 + フィルタ Zod スキーマ + 戻り値型 を全てここに集約する。 |
| [クライアント-ts](./クライアント-ts.md) | クライアント側 fetch ヘルパー。フロントエンドの hook / Server Component から呼ぶ。 |
| [サービス-ts](./サービス-ts.md) | トランザクション境界を持ち、`query.ts` / `db.ts` の関数を組み合わせて業務の単位を実行するビジネスロジック層 |
| [プロキシ](./プロキシ.md) | Next.js 16 で `middleware.ts` → `proxy.ts` にリネーム（export 関数名も `proxy`）。配置はプロジェクト直下。 |
| [ルート-ts](./ルート-ts.md) | HTTP ハンドラ（GET / POST / PATCH / DELETE）。`withRouteErrorHandling` でラップし、認証 → Zod パース → `service.ts` 呼び出しの順に書く。 |
| [レートリミット](./レートリミット.md) | 第一選択は Upstash Ratelimit（Redis ベース・Edge 対応）。`@upstash/ratelimit` + `@upstash/redis`、env は `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN`。 |
| [ローカルYAML開発DB](./ローカルYAML開発DB.md) | ローカル開発用 YAML データストア |
| [冪等性](./冪等性.md) | Next.js App Router — Idempotency |
| [認証アクション](./認証アクション.md) | ログイン・サインアップ・ログアウトの Server Action 群。 |
| [認証クライアント](./認証クライアント.md) | ブラウザから Better Auth のセッションを扱う hook |
| [認証コンテキスト](./認証コンテキスト.md) | すべての `route.ts` / Server Action / Server Component が認証を取る統一エントリポイント。 |
| [認証スキーマ](./認証スキーマ.md) | Better Auth が要るテーブルとアプリ固有の profile の定義 |
| [認証セットアップ](./認証セットアップ.md) | 採用認証プロバイダ: Better Auth（DB 非依存・TypeScript ファースト）。 |

<!-- /table -->
