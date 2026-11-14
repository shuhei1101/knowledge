# 手書きのテンプレートと schemas/design の AI slop の単語と、目次のスキーマに残る dev/ を修正する

## 概要

手書きのテンプレートと `schemas/design/` に残る AI slop の単語を対応表の OK の単語へ修正し、目次のスキーマの説明に残る `dev/` を `docs/` だけにする。

## 背景

束の [#335](https://github.com/shuhei1101/knowledge/issues/335) の要望で、次の 2 件を 1 本の作業 PR で行う。

- [#261](https://github.com/shuhei1101/knowledge/issues/261): [PR #257](https://github.com/shuhei1101/knowledge/pull/257) で書き換えなかった手書きのテンプレートの文と `schemas/design/` に、AI slop の単語が残っている。PR #257 のスコープ外からフォルダごとに切り出した 1 件
- [#332](https://github.com/shuhei1101/knowledge/issues/332): `schemas/design/index.schema.yaml` の説明が、ai-monitor#3307 で廃止された `dev/` を記載したままになっている。[PR #325](https://github.com/shuhei1101/knowledge/pull/325) のスコープ外から切り出した 1 件

## 計画書

| ファイル | 中身 |
| --- | --- |
| `要件.md` | 要望の整理 |
| `文書.md` | 文書の計画書 |
