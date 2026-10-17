# Drizzle — マイグレーション運用

`drizzle-kit` を使った schema → SQL migration → DB 適用の流れ。

破壊的変更の手順:

1. アプリケーション側で旧カラム参照を全て削除（or 二重書き対応）
2. デプロイ → 旧コードが本番に残らないように
3. `pnpm drizzle-kit generate` で削除 migration 生成
4. 適用

- schema 変更後は必ず `generate` → 確認 → `migrate`
- production 自動適用 NG（手動 / 専用 job）
- マイグレーションファイルは git にコミット
- 生成された SQL は 手で編集 OK（だが schema.ts と矛盾しないこと）
- Enum 値は削除できない（追加と改名のみ）。削除は新しい型へ列を移して旧型を drop する
