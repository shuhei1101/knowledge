# llm

python/llm の規約

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [Instructor](./Instructor.md) | LLM 出力を Pydantic モデルとして受け取るには Instructor を使う（スキーマ検証 + リトライ内蔵）。 |
| [コストとキャッシュ](./コストとキャッシュ.md) | LLM の呼び出しのコストの計測とキャッシュ |
| [プロバイダー](./プロバイダー.md) | LLM API（Claude / OpenAI / Gemini 等）を関数で抽象化して注入できるようにする。 |
| [プロンプトローダー](./プロンプトローダー.md) | `prompts/{id}.yaml` を読み、`when` に当たる部品の `text.en` を Jinja2 でレンダリングして 1 つのプロンプトに組み立てる。書き方は [プロンプトファイル](../../prompt/プロンプトファイル.md)。 |
| [例外とリトライ](./例外とリトライ.md) | リトライ可否を例外の型で判断できるよう `LlmError` ベースで分類する。 |

<!-- /table -->
