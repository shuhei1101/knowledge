# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/interface/IF-352-1.yml.yaml](https://github.com/shuhei1101/knowledge/blob/38bbcf6/docs/interface/IF-352-1.yml.yaml) | テストの全件実行のワークフロー。`constraints` の所要時間の `notes` が判定フローチャート『タイムアウトの決め方』の旧番号 `※5` を参照する | 更新対象 |
| ドキュメント | [docs/flowchart/flowchart-timeout.yaml](https://github.com/shuhei1101/knowledge/blob/38bbcf6/docs/flowchart/flowchart-timeout.yaml) | 判定フローチャート『タイムアウトの決め方』。結果のノード `r5`「実測の 10 倍か外側の作業の上限」に注記 `※[timeout-n5]` を持つ | 参照先。変更しない |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| IF-352-1 の所要時間の `notes` | 「判定フローチャート『タイムアウトの決め方』の ※5 で、」を「判定フローチャート [タイムアウトの決め方](id:flowchart-timeout) の結果「実測の 10 倍か外側の作業の上限」で、」に置き換える。後ろの「層 TL-3 の手元の実測（約 4 分）の 10 倍」は維持する | `timeout-minutes: 40` の値は変えない |
