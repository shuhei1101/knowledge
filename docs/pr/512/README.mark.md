# mdmark の記法を含む生成物の README の拡張子を .mark.md へ移す

## 概要

`docs/` の目次の README を、mdmark の記法で記載する文書の拡張子 `.mark.md` で生成し直す。

## 背景

[#331](https://github.com/shuhei1101/knowledge/issues/331) の要望。
[shuhei1101/mdmark#499](https://github.com/shuhei1101/mdmark/issues/499) で、mdmark の記法で記載する文書の拡張子を `.mark.md` にした。
knowledge で記法を含む `.md` は、AI Monitor の README の生成が出す目次と `docs/pr/` の記録で、どちらも AI Monitor が名前を決めていた。
[shuhei1101/ai-monitor#3427](https://github.com/shuhei1101/ai-monitor/issues/3427) で生成が `README.mark.md` を出すようになったため、目次を移せる。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
