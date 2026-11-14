# 規約・判定フローチャート・使い方・README・CLAUDE.md の dev-docs の記述を project-index に合わせ、規約『フック作成ガイド』に additionalContext だけを出す行を追加する

## 概要

規約・判定フローチャート・使い方・直下の `README.md`・`CLAUDE.md` に残る、文書の MCP・管理の MCP・配信元の登録を dev-docs が持つという記述を project-index に合わせる。
規約『フック作成ガイド』に、許可・拒否を判断せずに `additionalContext` だけを出す PreToolUse のフックの出力の行を追加する。

## 背景

束の [#340](https://github.com/shuhei1101/knowledge/issues/340) の要望で、次の 2 件を 1 本の作業 PR で行う。

- [#328](https://github.com/shuhei1101/knowledge/issues/328): shuhei1101/project-index#15・shuhei1101/dev-docs#163 で、文書の MCP・管理の MCP・配信元の登録が project-index へ移り、dev-docs は画面のサーバーになった。設計書と使い方『guide-setup-docs-mcp』は [PR #326](https://github.com/shuhei1101/knowledge/pull/326) で書き換えたが、規約・判定フローチャート・使い方・`README.md`・`CLAUDE.md` に dev-docs の記述が残っている
- [#330](https://github.com/shuhei1101/knowledge/issues/330): shuhei1101/mdmark#541 のフックが `permissionDecision` を返さずに `additionalContext` だけを出す。規約『フック作成ガイド』にこの場面の行が無い

## 計画書

| ファイル | 中身 |
| --- | --- |
| `要件.md` | 要望の整理 |
| `文書.md` | 文書の計画書 |
