# 開発ドキュメントのサイドバーのグループの分け方と、設計書のタイトルに種類の名前の前置きを付けない決まりを追加する

## 概要

エージェントが、dev-docs のサイドバーのグループを分けるかと何で分けるかを判定でき、設計書のタイトルに種類の名前・フォルダの名前の前置きを付けずに書けるようにする。

## 背景

[Issue #545](https://github.com/shuhei1101/knowledge/issues/545) の要望。
利用者が、dev-docs のサイドバーで「ER 図: 」のような前置きが付くことと、項目がフラットに並ぶことを報告した。
規約『開発ドキュメントのナビゲーション』（`dev-docs-navigation`）は「グループでまとめる・入れ子は 2 階層まで」を持つが、何件から・何で分けるかの決まりが無い。
設計書のスキーマのうち、設定・データ・データフロー・ER 図・状態遷移・ヒューマンエスカレーションの表・確認観点の表は、`title` の説明と `pattern` で種類の名前の前置きを求めている。
後続の [shuhei1101/aituber#136](https://github.com/shuhei1101/aituber/issues/136)・[shuhei1101/mindstella#543](https://github.com/shuhei1101/mindstella/issues/543)・[shuhei1101/ai-monitor#3510](https://github.com/shuhei1101/ai-monitor/issues/3510) が、この作業 PR の完了を待っている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
