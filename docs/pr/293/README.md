# 判定フローチャート『エージェントに渡す文・処理の置き場所』の例の差し替え・既存を使用するか新しく作るかの判定フローチャートの追加・docs/flowchart の AI slop の修正

## 概要

判定フローチャート『エージェントに渡す文・処理の置き場所』の ※3 の例を rule-inject の今の実体と合わせ、新しく作る関数・定数・部品を既存の使用・拡張・新規作成のどれにするかを判定フローチャートで決められるようにし、`docs/flowchart` に残る AI slop の単語を修正する。

## 背景

[#292](https://github.com/shuhei1101/knowledge/issues/292) は次の 3 件の束。

- [#258](https://github.com/shuhei1101/knowledge/issues/258): [shuhei1101/rule-inject#133](https://github.com/shuhei1101/rule-inject/pull/133)（マージ済み）で、rule-inject の新しいファイルの作り方の決まりが SessionStart の注入から MCP サーバーの instructions へ移った。※3 の「MCP を持たないプラグインの常に守る決まり（例: rule-inject の新しいファイルの作り方）」が実体と合わない
- [#250](https://github.com/shuhei1101/knowledge/issues/250): 新しく作る関数・クラス・定数・型・設定のキー・部品を、既存のものを使用するか・広げるか・新しく作るかを決める判定が無い。後続の [shuhei1101/ai-monitor#3184](https://github.com/shuhei1101/ai-monitor/issues/3184) が、この判定フローチャートを planner の手順から参照する
- [#262](https://github.com/shuhei1101/knowledge/issues/262): [#257](https://github.com/shuhei1101/knowledge/pull/257) で書き換えなかった `docs/flowchart` の文に、AI slop の単語が残っている

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | 反映作業の一覧 |
