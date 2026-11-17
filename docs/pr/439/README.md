# 開発ドキュメントのタブの並びとサイドバーのグループの決まりを規約に登録する

## 概要

各プロジェクトが、開発ドキュメントサーバー（dev-docs）のタブの並びとサイドバーのグループを、knowledge の決まりに従って配信の設定（`project-index.yaml` の `nav`）に記載できるようになる。

## 背景

[Issue #421](https://github.com/shuhei1101/knowledge/issues/421) の要望。
14 件の配信元の画面で、タブが 8〜34 件あって画面の幅に収まらず、入口の文書（使い方・公開ドキュメント）が右にあり、フォルダの目次（`index`）がサイドバーに同じ名前で並び、グループにしていないタブがある。
knowledge には、配信の画面のタブの並びとサイドバーのグループの決まりが無い（[ドキュメント管理](https://github.com/shuhei1101/knowledge/blob/1f63584/docs/rule/dev-document-management.yaml) の `group: 配信` は、配信の方式と `project-index.yaml` の行の決まりだけを持つ）。
各配信元の設定の修正は、後続の [#422](https://github.com/shuhei1101/knowledge/issues/422)（knowledge の配信元）などで行う。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
