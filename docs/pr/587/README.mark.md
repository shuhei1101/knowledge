# 書き込みの検査 knowledge-checks で textlint の違反を止める

## 概要

書き込みの検査 `knowledge-checks` で、書き込む文書に textlint を適用して違反を止め、`write_docs` の直コミットで textlint の違反が develop へ入らないようにする。

## 背景

[Issue #583](https://github.com/shuhei1101/knowledge/issues/583) の要望。
書き込みの検査は `knowledge-checks`（[scripts/knowledge_checks.py](https://github.com/shuhei1101/knowledge/blob/0f5168baf31c1f59187465f8a8f5a6251af79291/scripts/knowledge_checks.py)、`on: [write]`）の 1 件だけで、textlint を適用していない。
textlint を適用するのは全ての文書の検査（[scripts/check_all.py](https://github.com/shuhei1101/knowledge/blob/0f5168baf31c1f59187465f8a8f5a6251af79291/scripts/check_all.py)）だけのため、直コミットした違反は後の作業 PR で既存の違反として見つかる。
直コミットの [a19e05a](https://github.com/shuhei1101/knowledge/commit/a19e05a)・[857dbfc](https://github.com/shuhei1101/knowledge/commit/857dbfc) が `docs/knowhow/` の 3 文書へ違反 4 件を入れ、[#581](https://github.com/shuhei1101/knowledge/issues/581) で修正している。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) | 検査と変換のスクリプトの計画書 |
