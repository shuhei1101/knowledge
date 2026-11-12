# 規約『文章の書き方』の悪い例を書き戻し、話し合いで決めた文書の決まり 4 件を規約に追加する

## 概要

規約『文章の書き方』の原則の表の悪い例を NG の単語に戻し、話し合いで決めた文書の決まり 4 件（資料の本文・テンプレートと資料・設定の構造・VS Code 拡張機能の .vsix）を、該当する文書・設定を作るエージェントに注入される規約に追加する。

## 背景

[#306](https://github.com/shuhei1101/knowledge/issues/306) は次の 2 件の束。

| Issue | 背景 |
| --- | --- |
| [#301](https://github.com/shuhei1101/knowledge/issues/301) | [#296](https://github.com/shuhei1101/knowledge/pull/296) の AI slop の単語の置き換えで、規約『文章の書き方』の `word-choice-principle-02` の悪い例が `送信する・追加する・題` になり、原則の例として読めない。同じ commit で `writing-style-check-01`・`-02` の `group` も `文章の記載方法` に変わった |
| [#247](https://github.com/shuhei1101/knowledge/issues/247) | 話し合い（MindStella のワークスペース）で決めた文書の決まり 4 件が、そのワークスペースの `CLAUDE.md` にだけあり、knowledge の規約に無いため、ほかのリポジトリ・話し合いのエージェントに届かない |

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
