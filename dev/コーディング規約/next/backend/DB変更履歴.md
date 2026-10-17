# Drizzle — ハードデリート + 履歴テーブル

- ソフトデリート（`deletedAt`）は使わず、削除前にスナップショットを履歴テーブルへ退避してハードデリート。
- 削除系の全 service で履歴記録 → ハードデリート の順
- 履歴記録はトランザクション内（履歴 INSERT 成功 + DELETE 成功で同期）
- `snapshot` は jsonb
- `tableName` + `recordId` で復元時の照合
- `deletedBy` で誰が削除したかを追跡
