# 単一ファイルスクリプト

pyproject.toml を作らない簡易スクリプト（自動化・コンバート・レポート生成等）。パッケージ化が必要になったら py-project に昇格。

## 配置

ルート直下ではなく `scripts/`（or `tools/`）サブフォルダ。共通ヘルパーは `_common.py`。

## 必須要素

1. モジュール docstring: 1 行目で何をするか + 使い方
   - Usage はインデントなしでコピペ実行可能なコマンド、その上に `#` で説明、任意引数は `[角括弧]`
2. `from __future__ import annotations`
3. 引数は argparse でパース（パス等の即値ハードコード禁止）
4. `main() -> int` で終了コードを返し、`if __name__ == "__main__": sys.exit(main())`
5. トップレベルに処理を書かない（import しただけで実行されてしまう）
6. 出力は `print`（エラーは `file=sys.stderr`）— logging モジュールは使わない
   - このページが当たるファイルでは、`python/core/言語ルール.md` の `## ロギング`（`print` ではなく `logger`）より本ページを優先する
7. 想定例外は捕まえて専用の終了コード、未捕捉は `traceback.print_exc()`
8. コメント・print メッセージは日本語
