# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/interface/IF-352-1.yml.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/interface/IF-352-1.yml.yaml) | テストの全件実行のワークフロー | 変えない |
| 実装 | [.github/workflows/test.yml](https://github.com/shuhei1101/knowledge/blob/develop/.github/workflows/test.yml) | テストの全件実行 | 変えない |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| テストの全件実行 | ワークフローは変えない。全ての文書の検査は「Markdown のテンプレートの生成」を `uv run --frozen --script` で子プロセスとして起動し、dev-docs はスクリプトの依存の宣言とロックで固定したコミットを uv が取得する | ランナーは既に uv を入れている |
