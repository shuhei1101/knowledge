# TypeScript 風 Python — 関数ファースト設計

中心ドキュメント。関数ファースト + 型エイリアス + DTO + Protocol で書く。

- 振る舞いはモジュールレベルの関数、データは DTO
- クラスを書いてよいのは: DTO / ライブラリ要求（Middleware・BaseModel 継承・Enum 等）/ 長期保持のランタイム状態 のみ
- 「クラスを継承させて差し替え」はやらない（duck typing で済ます）

## 型エイリアス DI（基本パターン）

外部依存（LLM / TTS / HTTP / DB）は関数の型エイリアスで抽象化し、キーワード引数で注入する。
型は `types.py` に置き、`service.py` は型で受け、`main.py` で `partial` で配線する。テストでは mock 関数を注入するだけ。

- 実装（`openai_client.py` / `mock_client.py` 等）はベンダーごとに別ファイルの関数
- 注入する関数を切り替えるだけで本物 / モックが切り替わる

## インターフェース抽象化の 3 段階

| 段階 | パターン                                              | 用途                                          |
| ---- | ----------------------------------------------------- | --------------------------------------------- |
| 1    | 関数の型エイリアス（`type FindUser = Callable[...]`） | 1 機能の差し替え                              |
| 2    | `Protocol`                                            | 複数メソッド / 属性をまとめる（継承宣言不要） |
| 3    | `@overload`                                           | 戻り値が引数型で分岐（稀）                    |

## DTO の使い分け

<!-- table: data -->

| 用途                              | 推奨                                                |
| --------------------------------- | --------------------------------------------------- |
| 外部 HTTP リクエスト / レスポンス | `pydantic.BaseModel`                                |
| 設定（YAML / 環境変数）           | `pydantic_settings.BaseSettings`                    |
| LLM 構造化出力（Instructor）      | `pydantic.BaseModel`                                |
| CLI 引数の構造体                  | `pydantic.BaseModel` |
| 関数間の内部 DTO                  | `@dataclass(frozen=True, slots=True, kw_only=True)` |
| JSON 由来の dict をそのまま扱う   | `TypedDict`（`NotRequired` でオプション）           |
| 構造的型付け                      | `Protocol`                                          |

<!-- /table -->

- Pydantic は検証ありでやや重い → 外部境界に。dataclass は軽量 → 内部に
