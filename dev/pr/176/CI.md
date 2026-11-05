# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| 実装 | [.github/workflows/docs-check.yml](https://github.com/shuhei1101/knowledge/blob/develop/.github/workflows/docs-check.yml) | PR ごとに全ての文書の検査を動かす | markdownlint・textlint・yamllint を入れるステップだけを追加（呼び出しは `check_all.py`） |
| 実装 | [scripts/check_all.py](https://github.com/shuhei1101/knowledge/blob/develop/scripts/check_all.py) | 全ての文書の検査 | lint の CLI の在りかの確認と呼び出しを追加 |
| ドキュメント | [dev/設計書/インターフェース定義/scripts/全ての文書の検査.py.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%95%E3%82%A7%E3%83%BC%E3%82%B9%E5%AE%9A%E7%BE%A9/scripts/%E5%85%A8%E3%81%A6%E3%81%AE%E6%96%87%E6%9B%B8%E3%81%AE%E6%A4%9C%E6%9F%BB.py.yaml) | 全ての文書の検査のインターフェース定義（IF-72-3） | lint の検査と CLI の欠けの流れを追加 |
| ドキュメント | [dev/設計書/モジュール構成/scripts/check_all.py.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%83%A2%E3%82%B8%E3%83%A5%E3%83%BC%E3%83%AB%E6%A7%8B%E6%88%90/scripts/check_all.py.yaml) | 全ての文書の検査のモジュール構成 | lint の呼び出しの関数を追加 |
| ドキュメント | [dev/設計書/インターフェース定義/ci/文書の検査のワークフロー.yml.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%95%E3%82%A7%E3%83%BC%E3%82%B9%E5%AE%9A%E7%BE%A9/ci/%E6%96%87%E6%9B%B8%E3%81%AE%E6%A4%9C%E6%9F%BB%E3%81%AE%E3%83%AF%E3%83%BC%E3%82%AF%E3%83%95%E3%83%AD%E3%83%BC.yml.yaml) | 文書の検査のワークフローのインターフェース定義 | ステップと失敗の条件を追加 |
| ドキュメント | [dev/設計書/シナリオ/単一ユースケース/開発者が文書の違反を検査する.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E3%82%B7%E3%83%8A%E3%83%AA%E3%82%AA/%E5%8D%98%E4%B8%80%E3%83%A6%E3%83%BC%E3%82%B9%E3%82%B1%E3%83%BC%E3%82%B9/%E9%96%8B%E7%99%BA%E8%80%85%E3%81%8C%E6%96%87%E6%9B%B8%E3%81%AE%E9%81%95%E5%8F%8D%E3%82%92%E6%A4%9C%E6%9F%BB%E3%81%99%E3%82%8B.yaml) | CI で全ての文書を検査するシナリオ | lint の検査の流れを追加 |
| ドキュメント | [dev/設計書/開発コマンド/開発コマンド.yaml](https://github.com/shuhei1101/knowledge/blob/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E9%96%8B%E7%99%BA%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89/%E9%96%8B%E7%99%BA%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89.yaml) | 開発で使うコマンド | 検査の分類にコマンドを追加 |
| ドキュメント | [dev/設計書/外部ライブラリ/](https://github.com/shuhei1101/knowledge/tree/develop/dev/%E8%A8%AD%E8%A8%88%E6%9B%B8/%E5%A4%96%E9%83%A8%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA) | 使う外部ライブラリ・CLI | markdownlint-cli2・textlint・yamllint を追加 |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| markdownlint | markdownlint-cli2 を CI で動かす。区切り線（`---`）・太字（MD036 など）を『Markdown 編集規約』に合わせて設定する | 1 文 1 行は textlint の `textlint-rule-one-sentence-per-line`、文中の太字は markdownlint のカスタムルール（`## PoC 結果`） |
| textlint | textlint と textlint-rule-preset-ja-technical-writing を CI で動かす | 単語の対応表は slop-check（#135）が持つため、prh は入れない |
| yamllint | yamllint を CI で動かし、引用符の無い値の取り違え（`#` 以降がコメントになるなど）を検出する | 設定は `.yamllint.yaml` |
| 当てる範囲 | `check_all.py` が文書の Markdown の項目を 1 項目ずつ取り出して markdownlint・textlint を呼ぶ | `## PoC 結果` |
| PoC 検証 | PoC PR（`poc/rules/lint-cli`）で次を確かめる。行の対応: 文書の Markdown の項目を 1 項目ずつ一時の `.md` にして当て、CLI の行に `iter_strings` の項目の開始行を足して元の YAML の行で出せるか。1 文 1 行: まず既存の `textlint-rule-one-sentence-per-line` に当て、成功条件（`A です。B です。` を違反にし、`。` で終わる行・コードブロック・表のセルは違反にしない）を満たさないときだけカスタムルールを作る。文中の太字: markdownlint のカスタムルール（既存のルールが無い）。既存の違反: `docs/` の全ての文書に当てた違反の件数をルールごとに記録し、断片であることが原因のルール（MD041 など）を無効にした後の件数で、この PR で修正できる量かを判断する。所要時間: 今の `check_all.py` を実測し、既存の検査と 3 つの CLI の合計が 5 分（ジョブの `timeout-minutes`）以内か。yamllint の `comments` を `level: error` にした終了コード 1 は、レビューで確認済みのため検証しない | 結果は `## PoC 結果` に記録する。PoC は `check_all.py` の外から CLI を呼ぶため、結論に効く違いは所要時間（並列の読み込みを通さない）だけで、行の対応・検出の可否は構成によらない。項目ごとに当てる方式が成り立ったら、シナリオの `minimal_guarantee`・異常シナリオの `expected` と要件.md の案 A の「文書を変換した Markdown」を「文書の Markdown の項目」に修正する |
| 既存の違反 | yamllint の 6 件と、markdownlint の記法が原因の違反（`## PoC 結果`）の設定はこの PR で修正する。文の違反があるルールは警告にし、#145 の移行の後に失敗させる設定へ切り替える | 要件.md の `### 検査ツール` |

## PoC 結果

| 検証構成 | 成功条件 | 結果 | PoC PR | 補足 |
| --- | --- | --- | --- | --- |
| 行の対応（Markdown の項目を 1 項目ずつ `.md` にし、CLI の行に `iter_strings` の開始行を足す） | `body` の 3 行目の太字だけの段落の MD036 が元の YAML の行で出る | ✅ YAML の 26 行目で出た | [#177](https://github.com/shuhei1101/knowledge/pull/177)（closed） | 採用 |
| 1 文 1 行（`textlint-rule-one-sentence-per-line` v2.0.0） | `A です。B です。` を違反にし、`。` で終わる行・コードブロック・表のセルは違反にしない | ✅ 1 行目だけ違反 | 同上 | 採用。カスタムルールは作らない |
| 文中の太字（markdownlint-cli2 v0.24.0 のカスタムルール `no-inline-strong`） | 文中の `**太字**` を違反にし、インラインコードの中の `**` は違反にしない | ✅ 文中と段落全体の太字が違反、インラインコードは違反なし | 同上 | 採用 |
| 所要時間（`docs/` の 263 件・Markdown の項目 2,155 件） | 既存の検査と 3 つの CLI の合計が 5 分以内 | ✅ 51 秒（既存の検査 4 秒、markdownlint 9 秒、textlint 34 秒、yamllint 3 秒、書き出し 3 秒） | 同上 | WSL の `/mnt/c` での実測 |
| yamllint の既存の違反（`docs`・`schemas`・`dev-docs.yaml`・`rules.yaml`。`default` に `comments: error`、`line-length`・`document-start` を無効） | この PR で修正できる量か判断できる | ✅ 6 件（truthy 3・trailing-spaces 2・new-line-at-end-of-file 1）。3 秒 | 同上 | この PR で修正する |
| markdownlint・textlint の既存の違反（`docs/`） | ルールごとの件数で、この PR で修正できる量か判断できる | ❌ 1,202 件。記法が原因のルールを除いても約 850 件 | 同上 | 下の表 |

既存の違反のルールごとの件数（MD041・MD013 は断片であることが原因のため無効にした後）:

| 区分 | ルール | 件数 | 扱い |
| --- | --- | --- | --- |
| 記法が原因 | MD033（表のセルの `<br>`。『Markdown 編集規約』が許す） | 172 | `br` を許可する |
| 記法が原因 | MD060（表の空白の揃え方） | 106 | 無効にする |
| 記法が原因 | MD029（番号付きリストの番号） | 38 | 無効にする |
| 記法が原因 | MD038（書き方の例のコード `` `## ` `` など） | 25 | 無効にする |
| 記法が原因 | MD052（`[!code ++]` などの部品の記法） | 6 | 無効にする |
| 文の違反 | one-sentence-per-line | 218 | 警告にする（要件.md の `### 検査ツール`） |
| 文の違反 | no-inline-strong | 200 | 同上 |
| 文の違反 | MD032・MD040・MD031 | 127 | 同上 |
| 文の違反 | ja-technical-writing（ja-no-mixed-period・sentence-length・no-doubled-joshi など） | 307 | 同上 |

結論: 成立（行の対応・検出・所要時間）。
既存の違反は約 850 件で、263 件の文書の大半に及ぶため、この PR では修正しきれない。
文の違反があるルールは警告にする（要件.md の `### 検査ツール`）。
最小再現コードの要点は PoC PR の `poc/run.py`（`collect` が `iter_strings` で `body` の項目と開始行を取り出して 1 項目 1 ファイルに書き、`main` が CLI の行に開始行を足して `{ファイル}:{行}: {項目のパス}: {ルール}: {内容}` で出す）と `poc/no-inline-strong.mjs`（micromark のトークンの `strong` を違反にする 20 行）。

## 設計書の確定コミット

| 工程 | 範囲 | 補足 |
| --- | --- | --- |
| 単一ユースケース設計 | `cdffaeb..5b0927b` | - |
| 単一ユースケース設計 | `90caae6..cd7a41f` | レビューの指摘の修正 |
| 単一ユースケース設計 | `a388d50..412047f` | 合格後の任意の指摘と、PoC の結果（文書の Markdown の項目に当てる）の反映 |

## テスト結果

未実施。
