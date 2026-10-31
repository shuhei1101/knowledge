# Knowledge

どのプロジェクトでも共通で使うコーディング規約・テンプレートを置くリポジトリ。

## ドキュメント

実体は [docs/](./docs/) の YAML にある。
種類（rule・template・flowchart・guide・skill）ごとのフォルダに 1 トピック 1 ファイルで置き、スキーマは [schemas/](./schemas/) にある。
使い方は [使い方](./docs/guide/)。
dev-docs では直下の [dev-docs.yaml](./dev-docs.yaml) で配信し、配信元の ID は `knowledge`。
文書の検査と Markdown への変換のスクリプトは [scripts/](./scripts/) にあり、`dev-docs.yaml` の `validators[]`・`converters[]` と CI から呼ぶ。

着手前に、触るファイルに当たる規約を直下の [rules.yaml](./rules.yaml) で引いて読む。
