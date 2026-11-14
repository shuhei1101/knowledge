# Knowledge

どのプロジェクトでも共通で使用するコーディング規約・テンプレートを配置するリポジトリ。

ドキュメント: [https://shuhei1101.github.io/knowledge/](https://shuhei1101.github.io/knowledge/)

## 使い方

- project-index の配信元に登録すると、どの作業場所からでも dev-docs の画面と project-index の文書の MCP（`source: knowledge`）で文書を検索・取得できる（[knowledge を project-index の配信元に登録する](./docs/guide/guide-setup-docs-mcp.yaml)）
- ファイルを触ったときにヒットする規約を案内させるときは、rule-inject の索引を適用する（[規約の索引を適用する](./docs/guide/guide-setup-apply-rule-index.yaml)）
- 書き込んだ中身にある AI slop の単語と置き換え先を通知させるときは、プラグイン slop-check を追加する（[knowledge のプラグインを入れる](./docs/guide/guide-setup-install-plugin.yaml)）

## 文書の検査

[dev-docs.yaml](./dev-docs.yaml) が指す全ての文書に、スキーマの検査と、スキーマで見られない決まり（ID の重複・参照の実在・mermaid の文法・対応表の `examples` が照合と合うか）の検査を適用する。
対応表のコピー（`plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json`）が原本と一致するかも確認する。
検査のスクリプトは [scripts/](./scripts/) にある。

```bash
uv sync --script scripts/check_all.py
uv run --frozen --script scripts/check_all.py
```

1 行目は初回だけ実行する。
mermaid の検査に使用する `@probelabs/maid` を、PATH から検索できる場所（WSL では Linux 側のファイルシステム）に配置しておく。
