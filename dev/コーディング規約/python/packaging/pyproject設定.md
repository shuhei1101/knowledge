# pyproject.toml 標準テンプレート

ruff / mypy / pyright の設定値は `core/スタイル.md` を参照（重複定義しない）。

```toml
[project]
name = "mypkg"
version = "0.1.0"
description = "短い説明（1 行）"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"

dependencies = [
    "pydantic",
    "pydantic-settings[yaml]",
    "httpx",
]

[dependency-groups]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "mypy",
    "ruff",
]

[project.scripts]
mypkg = "mypkg.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mypkg"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = ["-ra", "--import-mode=importlib", "--strict-markers", "--strict-config", "-W", "error"]
markers = [
    "external: real external-service connectivity tests (requires --run-external)",
]
```

## ポイント

- src レイアウト（`src/mypkg/`）
- テストツールは `[dependency-groups]` の `dev` に分離
- build backend は `hatchling`
- 依存の追加方法・実行は `packaging/依存パッケージ管理.md`
- `.gitignore` には `.venv/` `.env` `__pycache__/` 各種キャッシュ `dist/` を入れる
