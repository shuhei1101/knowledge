# app/api/v{N}/{resource}/query.ts

読み取り（SELECT）専用ファイル。SELECT 関数群 + フィルタ Zod スキーマ + 戻り値型 を全てここに集約する。

## ルール

- SELECT 関数だけを置く（INSERT / UPDATE / DELETE は `db.ts`）
- フィルタ Zod スキーマ + 型 もここで定義（route.ts / client.ts から共有）
- 戻り値型 もここで定義（`ResourceDetail` 等）
- 失敗は `QueryError` で包む（`DatabaseError` ではない）
- 引数は オブジェクト（`{ db, userId, params }`）
- 関数名は `fetch{Feature}` プレフィックス
- 複雑な JOIN・並列取得 (`Promise.all`) を積極利用
- 重複排除のため `groupBy` を使う（必要なら）
- 結果を構造化する private helper（`buildXxx`）は同ファイル内
- `canEdit` 等の権限フラグもサーバーで計算してレスポンスに含める

## 命名

- `fetch{Feature}` — 単体取得
- `fetch{Feature}s` / `fetch{Feature}List` — 一覧
- `fetch{Feature}By{Key}` — 特定キーでの取得
- `count{Feature}` — 件数だけ
- `exists{Feature}` — boolean
- Schema: `{Feature}FilterSchema`, `{Feature}SortSchema`, `{Feature}SearchParamsSchema`
- 戻り値型: `{Feature}Detail`, `{Feature}WithChildren` 等
