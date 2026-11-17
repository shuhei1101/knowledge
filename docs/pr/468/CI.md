# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/interface/IF-352-1.yml.yaml](https://github.com/shuhei1101/knowledge/blob/38bbcf6/docs/interface/IF-352-1.yml.yaml) | テストの全件実行のワークフロー。`constraints` の所要時間の `notes` が判定フローチャート『タイムアウトの決め方』の旧番号 `※5` を参照する | 更新対象 |
| ドキュメント | [docs/flowchart/flowchart-timeout.yaml](https://github.com/shuhei1101/knowledge/blob/38bbcf6/docs/flowchart/flowchart-timeout.yaml) | 判定フローチャート『タイムアウトの決め方』。結果のノード `r5`「実測の 10 倍か外側の作業の上限」に注記 `※[timeout-n5]` を持つ | 参照先。変更しない |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| IF-352-1 の所要時間の `notes` | 「判定フローチャート『タイムアウトの決め方』の ※5 で、」を「判定フローチャート『タイムアウトの決め方』の結果「実測の 10 倍か外側の作業の上限」で、」に置き換える。後ろの「層 TL-3 の手元の実測（約 4 分）の 10 倍」は維持する | `timeout-minutes: 40` の値は変えない。`notes` は Markdown でない文字列の項目のため、`id:` のリンクにしない |

## テスト結果

### 単体

なし。
変更は設計書の `notes` の文言だけで、規約『V字モデル』の対応表で対応する単体テストが無い。

### 結合

なし。
コードと workflow を変えず、関係する結合テストが無い。

### 全ての文書の検査

| コマンド | 結果 | 補足 |
| --- | --- | --- |
| `uv run --frozen --script scripts/check_all.py` | ✅ | 400 件の文書で違反 0 件・警告 0 件<br>`テスト結果/20261117183104_a620fc6_全ての文書の検査.log` |
