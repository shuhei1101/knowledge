# concurrency

python/concurrency の規約

## 目次

| ページ | 概要 |
| --- | --- |
| [並列処理](./並列処理.md) | GIL 前提で設計する（フリースレッドビルド・subinterpreters を使うときは、[Python のドキュメント](https://docs.python.org/3/howto/free-threading-python.html) と依存ライブラリで対応状況を確かめる）。 |
| [非同期処理](./非同期処理.md) | Python 3.12+ の asyncio 機能を前提に書く。 |
