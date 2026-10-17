# pyproject.toml 標準テンプレート

ruff / mypy / pyright の設定値は `core/スタイル.md` を参照（重複定義しない）。

```toml
[project]
name = "mypkg"
version = "0.1.0"
description = "短い説明（1 行）"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }

dependencies = [
    "pydantic>=2.6",
    "pydantic-settings>=2.2",
    "httpx>=0.27",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.1",
    "mypy>=1.8",
    "ruff>=0.5",
]

[project.scripts]
mypkg = "mypkg.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mypkg"]

[tool.uv]
managed = true

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = ["-ra", "--strict-markers", "--strict-config", "-W", "error"]
markers = [
    "external: real external-service connectivity tests (requires --run-external)",
]
```

## ポイント

- src レイアウト（`src/mypkg/`）でテストとパッケージの混同を防ぐ
- テストツールは `[dependency-groups]` の `dev` に分離（本番イメージに pytest を混入させない）
- `[project.scripts]` で `pip install` 後に CLI 起動可能
- build backend は `hatchling` 推奨（setuptools より設定が短い）
- 運用は uv: `uv init --package` / `uv add` / `uv add --dev` / `uv sync` / `uv run pytest`
- `.gitignore` には `.venv/` `.env` `__pycache__/` 各種キャッシュ `dist/` を入れる
