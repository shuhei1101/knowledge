# 規約とノウハウの届け方の記載と規約の索引・エイリアスの補強、UI の規約への状態ごとの色の差の確認を追加する

## 概要

エージェントが、知見を規約とノウハウのどちらに登録し、どう届けるか（規約は rule-inject の索引、ノウハウはエイリアスとタグ）を knowledge の文書で判断でき、今の規約が該当する操作のときに届くようにする。
あわせて、画面を作成・修正したエージェントが、選択中・ホバー・目立たせる要素がほかの状態と見分けられることをスクリーンショットで確認するようにする。

## 背景

[Issue #549](https://github.com/shuhei1101/knowledge/issues/549) は [#546](https://github.com/shuhei1101/knowledge/issues/546) と [#547](https://github.com/shuhei1101/knowledge/issues/547) の束。

- #546: 利用者が、規約は極力 rule-inject で該当する操作のときに参照を強制し、ノウハウは rule-inject を使用せずエイリアスとタグで任意に案内する、という基準を示した。規約『ドキュメント管理』の `knowhow-01` は分け方と「ノウハウは rules.yaml に掲載しない」までで、届け方の違いが無い。`docs/rule/` の規約のうち `rules.yaml` に無いものと、`aliases` を持たないものが多い
- #547: MindStella の画面を React に置き換えた後、タブ・切り替えの選択中とホバーの色が薄く、どれを選んでいるかが見分けにくかった（[shuhei1101/mindstella#671](https://github.com/shuhei1101/mindstella/issues/671)）。knowledge の UI の規約のスクリーンショットの確認は、規約『業務画面のUI要素』の PC 幅とスマホ幅だけ

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
