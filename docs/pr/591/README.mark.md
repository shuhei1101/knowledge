# 書き込みの検査 knowledge-checks で markdownlint-cli2・yamllint・mdmark の map の点検の違反も止める

## 概要

書き込みの検査 `knowledge-checks` で、書き込む文書に markdownlint-cli2・yamllint・mdmark の map の点検も適用して違反を止め、`write_docs` の直コミットでこれらの違反が develop へ入らないようにする。

## 背景

[Issue #589](https://github.com/shuhei1101/knowledge/issues/589) の要望。
[#587](https://github.com/shuhei1101/knowledge/pull/587)（起点 [#583](https://github.com/shuhei1101/knowledge/issues/583)）で、書き込みの検査（[scripts/knowledge_checks.py](https://github.com/shuhei1101/knowledge/blob/e137163/scripts/knowledge_checks.py)、`on: [write]`）は textlint を適用するようになった。
全ての文書の検査（[scripts/check_all.py](https://github.com/shuhei1101/knowledge/blob/e137163/scripts/check_all.py)）が適用する残りの markdownlint-cli2・yamllint・mdmark の map の点検は、書き込みの検査では適用していない。
そのため直コミットした違反は、後の作業 PR で全ての文書の検査を回したときに既存の違反として見つかる。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) | 検査と変換のスクリプトの計画書 |
