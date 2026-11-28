# 画面設計・部品設計のスキーマに、規約にあるのに記載する欄が無い決まりの欄を追加し、各プロジェクトへ設計書を書き直す Issue を起票する

## 概要

画面を設計する人が、状態の保持・ペイン・ボタンのアイコン・狭い幅の出し分け・表とタブの機能・ダイアログの閉じ方・押した後の振る舞いなど、規約にある決まりを画面設計・部品設計の欄に記載でき、記載漏れを検査で見つけられるようになる。

## 背景

[Issue #602](https://github.com/shuhei1101/knowledge/issues/602) の要望。
画面設計のスキーマ（`schemas/design/screen.schema.yaml`）には、規約（`ui-input-wording`・`ui-layout`・`ui-button-label`・`ui-keyboard` など）にある決まりを記載する欄が 12 分類で無く、設計の時点で決定せずに実装で抜ける（例: aituber の [#312](https://github.com/shuhei1101/aituber/issues/312)・[#313](https://github.com/shuhei1101/aituber/issues/313)・[#314](https://github.com/shuhei1101/aituber/issues/314)）。
前提の [#600](https://github.com/shuhei1101/knowledge/issues/600)（[#603](https://github.com/shuhei1101/knowledge/pull/603)。要素の `kind` の enum と判別子）と [#601](https://github.com/shuhei1101/knowledge/issues/601)（[#604](https://github.com/shuhei1101/knowledge/pull/604)。規約に足りない決まり）は develop に入っている。
#600 の表のうち、今のスキーマに無い欄の種類ごとの必須・禁止はこの PR が扱う（[移した範囲](https://github.com/shuhei1101/knowledge/issues/602#issuecomment-7237360134)）。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書（画面設計・部品設計のスキーマ・テンプレート・チェックシート・規約）の計画書 |
| [反映作業](./反映作業/index.yaml) | 設計書のスキーマのタグの作成・各プロジェクトへの書き直しの Issue の起票 |
