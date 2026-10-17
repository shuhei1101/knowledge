# Drizzle — SQL Builder vs Relational Queries

- Drizzle は SQL Builder（低レベル） と Relational Queries（高レベル） の 2 つの API を持つ。
- 標準は **SQL Builder**
- Relational Query は「単体取得 + 1 階層 with」のみ採用
- 複雑な JOIN は **alias + groupBy + Promise.all** を駆使
- `db.execute(sql.raw(...))` は使わない（SQL Injection の温床）
- 動的 SQL が必要なら `sql\`...\`` テンプレートタグ（パラメータ化される）

<!-- table: data -->

| ケース                                     | 推奨                        |
| ------------------------------------------ | --------------------------- |
| 単純な「ID で 1 件取得 + 1 階層 with」     | Relational Query            |
| 一覧取得（フィルタ・ソート・ページング）   | SQL Builder                 |
| 複数 JOIN（3+ テーブル）                   | SQL Builder                 |
| エイリアス必要（同じテーブルを 2 回 JOIN） | SQL Builder                 |
| 重複排除（`groupBy`）                      | SQL Builder                 |
| 件数 + 行を並列で取る                      | SQL Builder + `Promise.all` |
| `relations()` を使った自然な書き味が欲しい | Relational Query            |

<!-- /table -->
