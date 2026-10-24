# Drizzle — 楽観的ロック

- `updatedAt` 比較で「他のユーザーによる先行更新」を検知する標準パターン。
  - 全 update に `updatedAt` 比較必須（楽観ロックなしの update 禁止）
  - `WHERE id = ? AND updatedAt = ?` の 両方一致 が条件
- 一致しない（`returning()` が空）→ `VersionConflictError` を投げる
- 更新時に `updatedAt` を 新しい時刻に書き換える（次の更新の基準に）
- `mode: "string"` の値をそのまま比較に使う（`Date` に変換すると精度が落ちる）
- 例外は `VersionConflictError` をそのまま投げ、それ以外を `DatabaseError` で包む
- `updatedAt` の精度（Postgres はマイクロ秒、JS の `Date` はミリ秒）で比較が食い違う場合は、`version: integer` 列を併用して比べる
- 外部公開 API は `ETag` ヘッダ + `If-Match` で比べる（不一致は 412、`If-Match` が無い更新は 428）
- internal API は `updatedAt` を JSON body に含めて送信する
