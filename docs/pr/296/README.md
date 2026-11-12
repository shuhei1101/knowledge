# 規約『フック』に PreToolUse の permissionDecision の決まりを追加し、rules.yaml のコンテナ構成・テストフィクスチャの paths と docs/rule の AI slop を修正する

## 概要

フックを作る・修正するエージェントが、PreToolUse のフックの出力に `permissionDecision` を記載するようにする。
あわせて、`rules.yaml` のテンプレート『コンテナ構成』『テストフィクスチャ』の `paths` とテンプレートの本文の配置の記述を `docs/` の下の置き場所へ揃え、`docs/rule` の規約に残る AI slop の単語を修正する。

## 背景

[#295](https://github.com/shuhei1101/knowledge/issues/295) は次の 3 件の束。

| Issue | 背景 |
| --- | --- |
| [#244](https://github.com/shuhei1101/knowledge/issues/244) | auto モードでは、PreToolUse のフックが `updatedInput` を `permissionDecision` なしで返すと、書き換えた呼び出しが拒否されうる。規約『フック』（`docs/rule/claude-hook.yaml`）に記載が無く、`rules.yaml` の `claude-hook.yaml` の行の `paths` はプラグインの `hooks/` の下のスクリプトに当たらない |
| [#255](https://github.com/shuhei1101/knowledge/issues/255) | `dev/` を廃止した [#253](https://github.com/shuhei1101/knowledge/pull/253) で移し先が決まらず、`rules.yaml` の 2 行とテンプレートの本文が `dev/設計書/` を指したまま残っている |
| [#260](https://github.com/shuhei1101/knowledge/issues/260) | [#257](https://github.com/shuhei1101/knowledge/pull/257) で書き換えなかった `docs/rule` の文に、AI slop の単語が残っている |

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
