# shared

python/shared の規約

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [エラー定義](./エラー定義.md) | すべてのドメイン例外は `AppError` を継承する単一階層（`shared/errors.py`）。docstring のみのシンプルなクラス定義。 |
| [ロガー](./ロガー.md) | `print` ではなく logger。出力は JSON Lines（1 行 1 JSON）で集計・grep・dashboard 連携を見据える。 |
| [型定義](./型定義.md) | 複数 feature で共有される型だけを置く。 |
| [定数](./定数.md) | 計算済みの不変値だけを置く。env で切り替える値は `shared/設定.md`。 |
| [設定](./設定.md) | 既定値・環境の値・checkout の上書き・環境変数を `Settings(BaseSettings)` で型安全に読む（`shared/settings.py`）。 |

<!-- /table -->
