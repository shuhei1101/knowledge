# 全ての文書の検査へ、map の点検・インターフェース定義と workflow の突き合わせ・SKILL.md と生成元の比較を追加する

## 概要

開発者が全ての文書の検査（`scripts/check_all.py`）を 1 回実行すると、map の図の誤り・workflow のインターフェース定義と workflow のファイルの食い違い・SKILL.md と生成元の食い違いも違反として分かるようになる。

## 背景

束 [#375](https://github.com/shuhei1101/knowledge/issues/375) の要望で、子 Issue は [#343](https://github.com/shuhei1101/knowledge/issues/343)・[#369](https://github.com/shuhei1101/knowledge/issues/369)・[#371](https://github.com/shuhei1101/knowledge/issues/371)。

- #343: [#337](https://github.com/shuhei1101/knowledge/pull/337) で maid の mermaid の検査を削除し、全ての文書の検査で map の誤りを見つけられなくなった。knowledge が採用する mdmark の `v0.8.0` には map の点検が無い
- #369: [#368](https://github.com/shuhei1101/knowledge/pull/368) で、入口が `trigger` のインターフェース定義と workflow のファイルの突き合わせをレビューで行うと決めた。Mermaid の図の中の step 名・分岐を取り出す仕組みがスクリプトに無いため切り出した
- #371: [#338](https://github.com/shuhei1101/knowledge/pull/338) で SKILL.md を `scripts/build_skills.py` の生成物にしたが、生成物と生成元の一致は検査していない

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書のサブシステム（設計書・外部ライブラリ・チェックシート・`README.md`）の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトとテストの計画書 |
