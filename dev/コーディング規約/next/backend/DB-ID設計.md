# drizzle/schema.ts — 主キー（ID）設計

- UUID は `sql\`gen_random_uuid()\`` をデフォルトに使う（Postgres ネイティブ）
- `generatedAlwaysAsIdentity()` は 不変（外部から指定不可）
- 主キーを `bigint` にする必要があるテーブル（数十億行）が出てきたら個別検討
- ULID / NanoID 等の独自 ID は 特別な理由がない限り使わない
