# drizzle/schema.ts — Relations と Index

- 外部キー定義、relations、index の付け方。
- 頻繁な WHERE / ORDER BY 対象 カラムに index
- 複合 index はクエリパターンに合わせる（カラム順は selectivity 高い順）
- 過剰な index は INSERT/UPDATE を遅くする → 必要なものだけ
- index 名は `{table}_{column}_idx` / `{table}_{cols}_unique`
- `onDelete` を明示（デフォルトに任せない）
- 外部キーは 必ず `references()` で宣言（手動 JOIN なし）
- 全外部キーに `relations()` を定義
- 全外部キーに `index()` を付ける
- ユニーク制約は `uniqueIndex` で複合キー対応

## onDelete の選び方

| Behavior    | 用途                                                |
| ----------- | --------------------------------------------------- |
| `cascade`   | 親消滅で子も消す（タグ・コメント・履歴）            |
| `restrict`  | 子が存在する間は親消せない（マスター ↔ データ）     |
| `set null`  | 親消滅で外部キーを null（任意関連、カテゴリ削除等） |
| `no action` | 制約だけ宣言、削除時に処理しない（基本使わない）    |
