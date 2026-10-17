# shared/css

- コンポーネントに属さない基盤スタイルだけを置く（コンポーネント CSS は `shared/components/`）
- 各ファイルの役割は `html/フォルダ構成.md` のツリーに従う
- エントリポイントは `layers.css`（`@layer` 順序宣言 + `@import` 集約）
