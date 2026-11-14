# テストの層の実行場所の判定フローチャートとテスト実行方法の変更と、workflow をインターフェース定義で設計するための変更をまとめて行う

## 概要

各プロジェクトが、テストの層ごとに GitHub Actions のランナーと手元のどちらで回すかを決めてテスト実行方法に記載でき、GitHub Actions の workflow をインターフェース定義で分岐ごとにテストできる構造で設計できるようにする。

## 背景

[#355](https://github.com/shuhei1101/knowledge/issues/355)（[#350](https://github.com/shuhei1101/knowledge/issues/350)・[#351](https://github.com/shuhei1101/knowledge/issues/351) の束）の要望。

- #350: 全プロジェクトの単体・結合テストが手元の WSL で走り、メモリが逼迫している。テスト実行方法の層に実行場所を持つ項目が無く、ランナーで回せるかを決める基準も無い。規約『Git フックと CI で動かすもの』は CI でテストを動かさないと定めている（[#323](https://github.com/shuhei1101/knowledge/pull/323)）
- #351: テンプレート『インターフェース定義』は `flows[].flow` を `sequenceDiagram` に決めており、前例の [IF-137-2](https://github.com/shuhei1101/knowledge/blob/ec26dc5/docs/interface/IF-137-2.yml.yaml) では workflow の条件と分岐が読み取れない
- 後続の [#352](https://github.com/shuhei1101/knowledge/issues/352)（knowledge 自身のテストを GitHub Actions へ移す）が、この 2 件を前提にする

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | develop へマージした後の設計書のスキーマのタグの作成 |
