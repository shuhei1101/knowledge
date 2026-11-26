# テスト実行方法

テスト種別ごとの実行コマンドと前提。

**ID**: TP-1

## 前提

- Python 3.12 と uv
- DB: PostgreSQL 16 のローカル起動（`docker compose up -d postgres`）

## 単体テスト（バック）

**ID**: TL-1

**説明**: pytest で実行する。DB / API に依存しない。

- 外部依存なし（純粋関数と Mock だけ）

**全件実行**

```bash
uv run pytest tests/unit/
```

**個別実行**

**単位**: ファイル

**コマンド**

```bash
uv run pytest {単体テストファイルパス}
```

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 実行場所 | runner |
| ランナーでの実行 | ```bash… |
| 並列にできる | ✓ |
<!-- /table -->

<!-- row-detail: 2 -->

```bash
run_url=$(gh workflow run test.yml --ref "$(git branch --show-current)" -f layer=unit | grep -o 'https://[^ ]*/actions/runs/[0-9]*') && run_id=${run_url##*/} && (n=0; until gh api "repos/{owner}/{repo}/actions/runs/$run_id?exclude_pull_requests=true" > /dev/null 2>&1; do n=$((n+1)); if [ $n -ge 10 ]; then echo "実行 $run_id を 10 秒参照できません" >&2; exit 1; fi; sleep 1; done) && (rc=0; gh run watch "$run_id" --exit-status > /dev/null || rc=1; gh run view "$run_id" --log; exit $rc)
```

<!-- /row-detail -->

## 外部疎通テスト

**ID**: TL-2

**説明**: 実 API に繋いで疎通を確認する。

- 実 API の認証情報を環境変数に設定する
- 料金と副作用が出ることを認識した上で実行する
- 誤実行を防ぐため `--run-external` を必須にする

**全件実行**

```bash
uv run pytest tests/external/ --run-external
```

**個別実行**

**単位**: テスト

**コマンド**

```bash
uv run pytest {外部疎通テストファイルパス} --run-external
```

**実行場所**: local

**外部への依存と費用**: テストごとの料金は外部API の設計書の料金を参照する

## lint

**ID**: TL-3

**説明**: ruff で linter・formatter の check を、mypy で型検査を、import-linter で依存の向きを検査する。型検査と依存の向きの検査はプロジェクト全体に回す。

- 検査の設定は `pyproject.toml` が持つ

**全件実行**

```bash
(rc=0; uv run ruff check . || rc=1; uv run ruff format --check . || rc=1; uv run mypy . || rc=1; uv run lint-imports || rc=1; exit $rc)
```

## 結合テスト（バック）

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| ID | TL-4 |
| 説明 | pytest と pytest-xdist で、ファイルの単位でプロセスに分けて実行する。共有の資源を取り合うテストは `serial_integration` のマーカーを付け、並列の後に並列数 1… |
| 全件実行 | ```bash… |
<!-- /table -->

<!-- row-detail: 2 -->

pytest と pytest-xdist で、ファイルの単位でプロセスに分けて実行する。共有の資源を取り合うテストは `serial_integration` のマーカーを付け、並列の後に並列数 1 で実行する。

<!-- /row-detail -->

<!-- row-detail: 3 -->

```bash
(rc=0; uv run pytest tests/integration/ -m "not serial_integration" -n {並列数} --dist loadfile; r=$?; [ $r -eq 0 ] || [ $r -eq 5 ] || rc=1; uv run pytest tests/integration/ -m serial_integration; r=$?; [ $r -eq 0 ] || [ $r -eq 5 ] || rc=1; exit $rc)
```

<!-- /row-detail -->

**個別実行**

**単位**: ファイル

**コマンド**

```bash
(rc=0; uv run pytest {結合テストのパス} -m "not serial_integration" -n {並列数} --dist loadfile; r=$?; [ $r -eq 0 ] || [ $r -eq 5 ] || rc=1; uv run pytest {結合テストのパス} -m serial_integration; r=$?; [ $r -eq 0 ] || [ $r -eq 5 ] || rc=1; exit $rc)
```

**実行場所**: local

- docs/pr/**
- README.md
- tests/unit/**

<!-- table: {"kind": "data"} -->
| パス | 理由 |
| --- | --- |
| tests/conftest.py | 全ての結合テストが使用するフィクスチャを持つ |
| uv.lock | 依存のバージョンが変わると、全ての結合テストの実行環境が変わる |
<!-- /table -->

<!-- table: {"kind": "data"} -->
| ソースのフォルダ | 結合テスト |
| --- | --- |
| src/app/mcp/** | tests/integration/mcp/ |
| docs/phase/** | tests/integration/docs/test_phase_docs.py |
<!-- /table -->

**並列の設定**

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 層の中で並列にできる | ✓ |
| 1 並列あたりのメモリ | 0.5 |
| 固定のメモリ | 2.5 |
| 並列数の上限 | 4 |
<!-- /table -->
