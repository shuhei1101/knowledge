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
| 確認 | 修正した conftest で workflow の E2E テスト（TL-6）を 1 つ実行し、実行の結論と step ごとの結論を受け取れることを確認する | 実行したテストと選んだ理由を `## テスト結果` に記載する |

## テスト結果

### 単体

なし。
変更は E2E テストの fixture（`tests/e2e/workflow/conftest.py`）で、規約『V字モデル』の対応表で関係する単体テストが無い。

### 結合

なし。
変更したファイルは結合テストの層（TL-3）が実行するコードでなく、関係する結合テストが無い。

### E2E

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/e2e/workflow/test_test_yml.py](https://github.com/shuhei1101/knowledge/blob/86c2469/tests/e2e/workflow/test_test_yml.py) | `test_normal` | 実行のみ | ✅ | 修正した `workflow_runner` で実行 [44064390556](https://github.com/shuhei1101/knowledge/actions/runs/44064390556) を起動し、参照できるまで待ってから watch して、結論 `success` と step ごとの結論を受け取った。検証用のブランチは削除済み<br>`テスト結果/20261117192411_86c2469_E2Eテスト.log` |

`test_normal` を選んだのは、`workflow_runner` の起動から結論の取得までを通る最短のフロー（入力 `layer=unit`）で、待ちの追加を確認するのに足りるため。
他の 3 つのフローは同じ `workflow_runner` を使い、待ちの処理に差が無いため実行しない。

### lint

✅ TL-1 の全件。ruff の check・format、pyright（0 errors）、actionlint が通過した。<br>`テスト結果/20261117192305_86c2469_lint.log`
