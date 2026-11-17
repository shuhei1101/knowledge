# 出典の URL が見つからなかった台本の技法（記録 R-3 の B・C・D・E、R-33・A-71）を、別の経路で出典を確認して種類「ノウハウ」の文書として登録する

## 概要

利用者とエージェントが、#481・#484 で出典の URL が見つからず登録されなかった台本の技法のうち、別の経路で出典を確認できたものを、knowledge の種類「ノウハウ」（`docs/knowhow/`）から参照できるようになる。

## 背景

[Issue #488](https://github.com/shuhei1101/knowledge/issues/488) の要望。
[#485](https://github.com/shuhei1101/knowledge/issues/485)・[#486](https://github.com/shuhei1101/knowledge/issues/486) を 1 本の作業 PR で行う束。
[#484](https://github.com/shuhei1101/knowledge/pull/484)（記録 R-3 の D・E）と [#481](https://github.com/shuhei1101/knowledge/pull/481)（記録 R-3 の B・C、R-33・A-71）は、`sources[].url` がスキーマで必須のため、出典の URL が見つからなかった技法を登録せず、スコープ外として切り出した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書のサブシステムの計画書 |
