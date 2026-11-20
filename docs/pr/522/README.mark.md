# FastAPI の規約に、MCP のツールと同じデータを返却する API の JSON のキーとエラーの構造の扱いを追加する

## 概要

FastAPI の API を実装する人が、MCP のツールと同じデータを返却する API で、JSON のキーとエラーの応答を MCP のツールに合わせてよいかを規約で判断できるようにする。

## 背景

[Issue #520](https://github.com/shuhei1101/knowledge/issues/520) の要望。
規約『入出力 Pydantic スキーマ』は API の JSON のキーを camelCase に、規約『認証と例外ハンドラ』はエラーの応答を RFC 9457 に統一すると定めている。
aituber の管理画面の API は同じデータを MCP のツールでも返却するため、キーを snake_case に、エラーを MCP のツールと同じ構造（例外の名前・種類・メッセージ・`details`）にした。
今の規約にはこの場合の扱いが無く、aituber の管理画面の API は規約に違反した状態になっている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
