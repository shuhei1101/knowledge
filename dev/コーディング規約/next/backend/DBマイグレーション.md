# Drizzle — マイグレーション運用

`drizzle-kit` を使った schema → SQL migration → DB 適用の流れ。

drizzle-kit は基本的に 追加系（ALTER TABLE ADD COLUMN）は自動、削除・型変更は 対話的確認 で生成。

破壊的変更の手順:

1. アプリケーション側で旧カラム参照を全て削除（or 二重書き対応）
2. デプロイ → 旧コードが本番に残らないように
3. `pnpm drizzle-kit generate` で削除 migration 生成
4. 適用

「コード変更 → schema 変更」の順を厳守。

- schema 変更後は必ず `generate` → 確認 → `migrate`
- 破壊的変更は コード側の参照削除を先
- production 自動適用 NG（手動 / 専用 job）
- マイグレーションファイルは git にコミット
- 生成された SQL は 手で編集 OK（だが schema.ts と矛盾しないこと）
- Enum 値削除は段階的に
