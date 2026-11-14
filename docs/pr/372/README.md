# 直下の dev-docs.yaml を project-index.yaml へ改名し、ファイル名の記述と端末の設定を合わせる

## 概要

knowledge の直下の配信の設定 `dev-docs.yaml` を `project-index.yaml` へ改名し、スクリプト・テスト・設計書・規約・使い方・`CLAUDE.md`・`README.md` のファイル名の記述と、端末の設定が指すパスを改名後のパスに合わせる。

## 背景

[#329](https://github.com/shuhei1101/knowledge/issues/329) の要望。
[#326](https://github.com/shuhei1101/knowledge/pull/326)（束 [#324](https://github.com/shuhei1101/knowledge/issues/324)）のスコープ外から切り出された。
project-index の develop は `project-index.yaml` が無いフォルダでだけ `dev-docs.yaml` を読み込むため、#326 では改名しなかった。
同じ改名は alias-inject で [shuhei1101/alias-inject#81](https://github.com/shuhei1101/alias-inject/pull/81) が行っている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書のサブシステム（設計書・規約・使い方・`CLAUDE.md`・`README.md`）の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトとテストの計画書 |
| [反映作業](./反映作業/index.yaml) | 端末の設定の書き換え |
