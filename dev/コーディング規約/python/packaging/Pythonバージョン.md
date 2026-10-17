# Python バージョン方針

- 極力高いバージョンを採用する。新規は最新安定版か 1 つ下（各版の状況は [Python のリリース状況](https://devguide.python.org/versions/)）
- `requires-python = ">=3.12"` を最低ライン（PEP 695 全面採用のため）
- 内製 / 限定配布ならマルチバージョンサポートはしない（互換 shim 不要・最新固定が楽）
- 固定は pyproject の `requires-python` + `.python-version`（`uv python pin 3.12`）

## 新機能の採用判断

新しい版で入った機能は、その版の [What's New](https://docs.python.org/3/whatsnew/) で実験的な扱いでないことと、依存ライブラリが対応していることを確かめてから採用する。

## 最低ラインを下げる場合の覚悟

3.10 等に下げると PEP 695 不可（`TypeAlias` 代用）・`Self` は typing_extensions・TaskGroup 不可など、メンテコストが跳ね上がる。レガシー連携が必須の場合のみ。
