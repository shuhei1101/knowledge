# ローカル開発用 YAML データストア

> 関数ごとに `type` で型を定義し、`query.ts` / `db.ts` の実装を本番（Drizzle）と
> ローカル（YAML ファイル）で差し替える。クラス・`interface`・Repository は使わない。
> データアクセスは `fetch{Feature}` / `insert{Feature}` などの素の関数で、`db` を引数で受け渡す。
> トランザクション境界は `service.ts` が持つ。

```
service.ts（transaction() でトランザクション境界）
   ↓ fetchResource({ db, id }) / insertResource({ db, record })
query.ts / db.ts  ← env で実装を切り替え
   ├─ *.drizzle.ts  → 本番（Supabase / Drizzle）。渡された db(tx) を使う
   └─ *.yaml.ts     → ローカル（data/dev/*.yaml）。db は無視
```

- 関数の型（`FetchResource` 等）を `types.ts` に定義し、両実装が同じ型を満たす
- `USE_YAML_DB=true` を `.env.local` に設定するだけで切り替わる
- トランザクション維持：本番は Drizzle の `db.transaction`、ローカルは YAML スナップショット/ロールバック + ロック（ロックとロールバックの決まりは [YAML](../../dev/YAML.md) の `## MCP からの書き込み`）
- YAML ファイルはスキーマと同じフィールドを持つ → 移行コストなし

```
app/api/v{N}/resources/
├── types.ts          # 関数ごとの型定義
├── query.ts          # 読み取りの切り替え（re-export）
├── query.drizzle.ts  / query.yaml.ts
├── db.ts             # 書き込みの切り替え（re-export）
├── db.drizzle.ts     / db.yaml.ts
└── service.ts        # トランザクション境界
app/(shared)/lib/
├── yamlStore.ts      # readTable / writeTable / runYamlTransaction（ロック+ロールバック）
└── transaction.ts    # transaction() / baseDb の env 切り替え
data/dev/resources.yaml   # ローカル開発データ（gitignore）
```

実装ファイル（`*.drizzle.ts` / `*.yaml.ts`）は env を見ない。本番ビルドに YAML 実装を混入させない（`USE_YAML_DB` のガードを守る）。
