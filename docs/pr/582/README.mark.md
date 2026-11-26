# ノウハウの 3 文書の textlint の違反 4 件を修正し、全ての文書の検査を合格させる

## 概要

ノウハウの 3 文書の textlint の違反 4 件を、記述の意味を変えずに修正し、全ての文書の検査を違反 0 件で合格させる。

## 背景

[Issue #581](https://github.com/shuhei1101/knowledge/issues/581) の不具合。
develop（`9837d11`）で全ての文書の検査（`uv run --frozen --script scripts/check_all.py`）を実行すると、`docs/knowhow/` の 3 文書で textlint の違反 4 件が出て、終了コード 1 で終わる。
違反は直コミットの [a19e05a](https://github.com/shuhei1101/knowledge/commit/a19e05a)・[857dbfc](https://github.com/shuhei1101/knowledge/commit/857dbfc) で入った。
[#580](https://github.com/shuhei1101/knowledge/pull/580) のドキュメント修正で全ての文書の検査を回したときに見つかった。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.mark.md) | 文書（ノウハウ）の計画書 |
