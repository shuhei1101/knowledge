# Knowledge

どのプロジェクトでも共通で使うコーディング規約・テンプレートを置くリポジトリ。

ドキュメント: [https://shuhei1101.github.io/knowledge/](https://shuhei1101.github.io/knowledge/)

## 使い方

- dev-docs の配信元に登録すると、どの作業場所からでも画面と MCP（`source: knowledge`）で文書を検索・取得できる（[knowledge を dev-docs の配信元に登録する](./docs/guide/guide-setup-docs-mcp.yaml)）
- ファイルを触ったときにヒットする規約を案内させるときは、rule-inject の索引を適用する（[規約の索引を適用する](./docs/guide/guide-setup-apply-rule-index.yaml)）
- 書き込んだ中身にある AI slop の単語と置き換え先を通知させるときは、プラグイン slop-check を入れる（[knowledge のプラグインを入れる](./docs/guide/guide-setup-install-plugin.yaml)）

## 文書の検査

[dev-docs.yaml](./dev-docs.yaml) が指す全ての文書に、スキーマの検査と、スキーマで見られない決まり（ID の重複・参照の実在・mermaid の文法・対応表の `examples` が照合と合うか）の検査を当てる。
対応表のコピー（`plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json`）が正本と一致するかも確かめる。
検査のスクリプトは [scripts/](./scripts/) にある。

```bash
uv sync --script scripts/check_all.py
uv run --frozen --script scripts/check_all.py
```

1 行目は初回だけ実行する。
mermaid の検査に使う `@probelabs/maid` を、PATH から引ける場所（WSL では Linux 側のファイルシステム）に入れておく。
