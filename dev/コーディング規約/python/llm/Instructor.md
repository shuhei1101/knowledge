# Instructor — Pydantic で構造化出力

LLM 出力を Pydantic モデルとして受け取るには Instructor を使う（スキーマ検証 + リトライ内蔵）。

- クライアントは `instructor.from_provider("{provider}/{model}")` で作る（非同期は `async_client=True`）
- `client.chat.completions.create(response_model=MySchema, max_retries=3, ...)` で
  - JSON 受信 → Pydantic 検証 → 失敗時は LLM に修正させて再試行
- スキーマの `Field(description=...)` が抽出精度に効くので書く。固定選択肢は `Literal`、ネスト・`list[...]` も可
- 再試行を使い切った検証失敗は、Instructor が送出する例外を呼び出し側へ伝える（`None` に変えない）
- 逐次表示には `create_partial(...)`（部分的に埋まったオブジェクトが yield される）

## Task-specific client パターン

特定タスク特化の関数として封じる:
`type ExtractEventFn = Callable[[str], Awaitable[ExtractedEvent]]` を定義し、`make_extract_event_fn(*, client, model) -> ExtractEventFn` で client / model をクロージャに隠す。呼び出し側は記事を渡すだけ。

## ファイル構成

タスクが小さければスキーマ + プロンプト + 関数を 1 ファイルにまとめてよい（短いプロンプトはコード内、長ければ `content/prompts/`）。
