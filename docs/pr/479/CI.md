# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| テスト | [tests/e2e/workflow/conftest.py](https://github.com/shuhei1101/knowledge/blob/e8a4af1/tests/e2e/workflow/conftest.py) | workflow の E2E テストの fixture。`_dispatch` で ID を取った直後に `_watch` が `gh run watch` を呼ぶ。`check=False` のため 404 はそこで止まらず、続く `gh run view` が失敗する | `_watch` の前に待ちを入れる |
| テスト実行方法 | [docs/test-procedure/TP-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/e8a4af1/docs/test-procedure/TP-72-1.yaml) | TL-6（E2E テスト）は手元で `pytest tests/e2e/workflow` を回す | 変えない |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 実行を参照できるまでの待ち | `gh api "repos/{owner}/{repo}/actions/runs/{ID}?exclude_pull_requests=true"` を 1 秒おきに最大 10 回試す関数を足し、`workflow_runner` の `_start` で `_dispatch` と `_watch` の間に呼ぶ | 回数と間隔はモジュールの定数にし、`run_runner` の記載例と同じ値にする |
| 参照できないとき | 10 回で参照できなければ、実行の ID を含むメッセージで `pytest.fail` する | - |
| 確認 | 修正した conftest で workflow の E2E テストを 1 つ実行し、実行の結論と step ごとの結論を受け取れることを確認する | 実行するテストは実装で決め、結合テストの実行範囲の表で reviewer の確認を受ける |

## テスト結果

（実装で記入する）
