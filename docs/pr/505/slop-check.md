# slop-check

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/scenario/SC-148-1.yaml](https://github.com/shuhei1101/knowledge/blob/9b5d599/docs/scenario/SC-148-1.yaml) | エージェントが書き込んだ中身の AI slop の単語を通知される | 利用者の画面への 1 行の表示を、設定で表示するときだけにする |
| ドキュメント | [docs/interface/IF-148-1.py.yaml](https://github.com/shuhei1101/knowledge/blob/9b5d599/docs/interface/IF-148-1.py.yaml) | 書き込んだ中身の照合 | 入力に表示の設定を追加し、`systemMessage` を出す条件に加える |
| ドキュメント | [docs/module/MOD-148-2.py.yaml](https://github.com/shuhei1101/knowledge/blob/9b5d599/docs/module/MOD-148-2.py.yaml) | slop-check / hooks / slop_check.py | 設定を取得する関数と、`systemMessage` を組み立てる条件を追加する |
| 実装 | [plugins/slop-check/hooks/post-tool-use/slop_check.py](https://github.com/shuhei1101/knowledge/blob/9b5d599/plugins/slop-check/hooks/post-tool-use/slop_check.py) | 書き込んだ中身の照合のフック | 203 行目でヒットがあれば常に `systemMessage` を出す |
| 実装 | [plugins/slop-check/hooks/hooks.json](https://github.com/shuhei1101/knowledge/blob/9b5d599/plugins/slop-check/hooks/hooks.json) | slop-check のフックの登録 | `_description` の `systemMessage` の記述を、設定で表示するときだけに合わせる |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 表示の設定 | 環境変数 `SLOP_CHECK_SHOW_ADDED` を追加し、`1` のときだけ表示する | 利用者が決めた（[確認ログ](./確認ログ.yaml)） |
| 通知の出力 | ヒットがあれば `additionalContext` は今のまま出し、`systemMessage` は設定が表示するときだけ出す | 値が `1` 以外のときは表示しない |
| テスト | 単体は設定の取得と出力の分岐、結合は設定の有無ごとにフックを子プロセスで起動して出力を確認する | `tests/unit/slop-check/`・`tests/integration/slop-check/` |

## 設計書の確定コミット

| 工程 | 範囲 | 補足 |
| --- | --- | --- |
| 単一ユースケース設計 | `9b5d599..2cb3cbb` | - |
| インターフェース定義設計 | `207644a..d440694` | 設定の配置先は案 B（ユーザー確認で決める） |
| インターフェース定義設計 | `7313bb9..8965295` | レビューの指摘の修正 |
| インターフェース定義設計 | `57ecdf1..e353c28` | ユーザーの決定（環境変数）の反映 |
| インターフェース定義設計 | `9c194e8..8a3ae31` | レビューの指摘の修正 |
| モジュール構成設計 | `7415a91..1fec4e8` | - |

## テスト結果

### 単体

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/unit/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/9267868/tests/unit/slop-check/test_slop_check.py) | 全実行 | 変更 | ✅ | Python 3.14 で `tests/unit` 301 テスト pass、Python 3.12 で `tests/unit/slop-check` 45 テスト pass（ランナー）<br>`テスト結果/20261119155848_9267868_単体テスト.log`。Red は `テスト結果/20261119155559_5f3dc3c_単体テスト.log`（`test_main` は、画面への 1 行を常に出す振る舞いが `slop_check.py` の `main` に [c5a8bf7](https://github.com/shuhei1101/knowledge/commit/c5a8bf7)（#338）からあるため実装の前から pass） |

### 結合テストの実行範囲

| 変更したファイル | 結果 | 実行する結合テスト | 結合テストが無いエントリーポイント |
| --- | --- | --- | --- |
| `docs/architecture/ARCH-72-1.yaml` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/guide/guide-setup-install-plugin.yaml` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/interface/IF-148-1.py.yaml` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/interface/README.md` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/interface/index.yaml` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/module/MOD-148-2.py.yaml` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/module/README.md` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/module/index.yaml` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/pr/505/README.md` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/slop-check.md` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/タスク一覧.yaml` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/テスト結果/20261119155559_5f3dc3c_単体テスト.log` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/テスト結果/20261119155639_5f3dc3c_lint.log` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/テスト結果/20261119155848_9267868_単体テスト.log` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/テスト結果/20261119155905_9267868_lint.log` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/反映作業/index.yaml` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/反映作業/画面への表示の設定/dry-run.log` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/反映作業/画面への表示の設定/切り戻し.py` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/反映作業/画面への表示の設定/実行.py` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/反映作業/画面への表示の設定/疎通確認.py` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/反映作業/画面への表示の設定/確認.py` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/文書.md` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/確認ログ.yaml` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/要件.md` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/pr/505/要件.yaml` | R7（PR ドキュメントは配信せず、結合テストから参照されない） | - | - |
| `docs/scenario/README.md` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/scenario/SC-148-1.yaml` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `docs/scenario/index.yaml` | R7（`tests/integration/scripts/` は `repo_factory` の一時のリポジトリで検査・変換を起動し、このリポジトリの文書を読まない） | - | - |
| `plugins/slop-check/hooks/hooks.json` | R7（`_description` だけの変更。フックの起動のしかたを読む結合テストは上と同じ） | `tests/integration/slop-check/test_slop_check.py` | - |
| `plugins/slop-check/hooks/post-tool-use/slop_check.py` | R7（一覧・対応表に無い。フックを子プロセスで起動する結合テストが参照する） | `tests/integration/slop-check/test_slop_check.py` | - |
| `tests/unit/slop-check/test_slop_check.py` | R7（単体テストで、結合テストから参照されない） | - | - |

実行する結合テストは `tests/integration/slop-check/test_slop_check.py` だけ。結合テスト作成の工程で、IF-148-1 の追加した流れ（`test_normal_when_display_not_set`・`test_normal_when_display_value_not_one`）を足し、`systemMessage` を期待する流れは子プロセスの環境に `SLOP_CHECK_SHOW_ADDED=1` を入れ、表示しない流れは子プロセスの環境から `SLOP_CHECK_SHOW_ADDED` を除いて起動する。

### 結合

| ファイル | メソッド | 変更種別 | 結果 | 補足 |
| --- | --- | --- | --- | --- |
| [tests/integration/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/5f238e6/tests/integration/slop-check/test_slop_check.py) | `test_normal_when_display_not_set`・`test_normal_when_display_value_not_one` | 新規 | ✅ | IF-148-1 の追加した流れ |
| [tests/integration/slop-check/test_slop_check.py](https://github.com/shuhei1101/knowledge/blob/5f238e6/tests/integration/slop-check/test_slop_check.py) | `test_normal`・`test_normal_when_edit`・`test_normal_when_edited_file_unreadable`・`test_normal_when_notebook_edit`・`test_normal_when_mcp_tool`・`test_normal_when_dev_docs_mcp_tool` | 変更 | ✅ | `systemMessage` を期待する流れを `show_added="1"` で起動するようにした |
| [tests/integration/slop-check/conftest.py](https://github.com/shuhei1101/knowledge/blob/5f238e6/tests/integration/slop-check/conftest.py) | `run_hook` | 変更 | ✅ | 子プロセスの環境から `SLOP_CHECK_SHOW_ADDED` を除き、`show_added` を指定したときだけ入れる |

ファイル全体で 13 passed（`テスト結果/20261119160745_5f238e6_結合テスト.log`。lint は `テスト結果/20261119160802_5f238e6_lint.log`）。親の環境に `SLOP_CHECK_SHOW_ADDED=1` を入れても 13 passed。TL-3 の `run_runner` は層の全件だけを回すため、表の範囲を `run_one` で手元で回した。
