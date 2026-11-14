# Knowledge

どのプロジェクトでも共通で使用するコーディング規約・テンプレートを配置するリポジトリ。

## ドキュメント

実体は [docs/](./docs/) の YAML にある。
種類（rule・template・flowchart・decision-table・checksheet・guide・skill・word-list）ごとのフォルダに 1 トピック 1 ファイルで配置し、スキーマは [schemas/](./schemas/) にある。
設計書のスキーマの原本は [schemas/design/](./schemas/design/) にあり、各プロジェクトは `design-schemas/v{メジャー}.{マイナー}.{パッチ}` のタグで指す。
スキーマを変える PR は、develop へマージした後にタグを上げる反映作業を持つ。
既存の設計書が検査を通らなくなる変更はメジャー、通ったままの変更はマイナー、検査の結果を変えない変更はパッチを上げる。
[docs/template/](./docs/template/) の設計書の種類のテンプレートの本文はスキーマから生成する。スキーマを変えたら `uv run --frozen --script scripts/build_templates.py` を実行し、テンプレートを一緒に commit する。
使用方法は [使い方](./docs/guide/)。
project-index では直下の [dev-docs.yaml](./dev-docs.yaml) で配信し、配信元の ID は `knowledge`。
文書の検査と Markdown への変換のスクリプトは [scripts/](./scripts/) にあり、`dev-docs.yaml` の `validators[]`・`converters[]`・手元のコマンド・GitHub Pages の配信のワークフローから呼ぶ。

着手前に、触るファイルに該当する規約を直下の [rules.yaml](./rules.yaml) で検索して参照する。
