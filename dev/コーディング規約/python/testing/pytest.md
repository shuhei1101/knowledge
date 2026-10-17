# pytest 規約

設定値（testpaths / asyncio_mode / addopts / markers）は `packaging/pyproject設定.md` の `[tool.pytest.ini_options]` を参照。

## 命名

- ファイル `test_*.py`、関数 `test_*()`。クラスは使わず関数で書く
- 単体テストは `test_{関数名}_when_{条件}`。
  条件分岐のない唯一のケースは `test_{関数名}` のみ。
  先頭が `_` の関数は `_` を外す（例: `_get_client` → `test_get_client_when_settings_missing`）
- 期待値（returns_x / raises_y 等）は名前に入れない。
  期待値が変わるたびに関数名まで変わるため、期待値は docstring とアサートに書く
- 結合 / E2E はフロー・シナリオ見出しと機械対応させる。
  `正常系` → `test_normal` / `正常系（{条件}）` → `test_normal_when_{条件}` / `異常系（{条件}）` → `test_error_when_{条件}`
  `{条件}` は英訳（ASCII）で書く（見出しは日本語のまま）。
  見出しを変えたら、対応するテスト関数名も揃える
- 外部疎通は `test_ext_{関数名}_when_{パラメータ値}`。
  バリエーションが 1 つだけなら `test_ext_{関数名}` のみ

## fixtures

- 共通 fixture は `conftest.py` に置く
- テスト用 `Settings` は fixture で env を上書きして生成
- 時刻固定は `NowFn` に固定時刻関数を渡す（`testing/モック.md`）
- Mock 関数（成功 / rate-limited 等）も fixture 化して注入

## parametrize

複数パターンは `@pytest.mark.parametrize`、ケース名は `pytest.param(..., id="empty")` で明示。

## 例外の検証

`pytest.raises` は例外の型を絞り、`match` でメッセージも確かめる。
ブロックの中には例外を起こす 1 文だけを置く。

## FastAPI ルート

`build_fastapi()` → `app.state.handlers` にテスト用 Handlers（Mock 注入済み）をセット → `TestClient` で叩く。

## マーカー

- ファイル全体は `pytestmark = pytest.mark.external`、関数単位は `@pytest.mark.slow` 等
- 選択実行は `pytest -m "not external"`
