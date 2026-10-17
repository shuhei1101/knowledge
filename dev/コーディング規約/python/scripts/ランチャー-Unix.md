# sh ランチャー

UNIX 系（Linux / macOS / WSL）で Python スクリプトを起動する `.sh` の規約。

## 標準テンプレート

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f .venv/bin/activate ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

mkdir -p log
TS=$(date +%Y%m%d-%H%M%S)
LOG="log/script-${TS}.log"

python script.py "$@" 2>&1 | tee "$LOG"
EXIT_CODE=${PIPESTATUS[0]}

echo
echo "(log: $LOG)"
echo "(exit: $EXIT_CODE)"
exit "$EXIT_CODE"
```

## 必須要素

| 要素                              | 理由                                                                                          |
| --------------------------------- | --------------------------------------------------------------------------------------------- |
| `#!/usr/bin/env bash`             | dash 環境を避けて bash 明示                                                                   |
| `set -euo pipefail`               | 失敗即停止・未定義変数検出・pipe 途中失敗を拾う（pipefail なしだと tee 成功で exit 0 になる） |
| `cd "$(dirname "$0")"`            | スクリプトの場所を基準に                                                                      |
| `"$@"`                            | クォート付き引数転送（`$@` / `$*` は空白入り引数で壊れる）                                    |
| `tee "$LOG"` + `${PIPESTATUS[0]}` | 画面 + ファイル同時出力、python 側の終了コード取得                                            |

- uv プロジェクトなら `uv run python script.py "$@"` 推奨
- HOST / PORT 等は `"${HOST:-127.0.0.1}"` で環境変数上書き可能に
- 出力メッセージは英語基本（UTF-8 標準なので日本語も可、プロジェクトで揃える）
- `chmod +x` を忘れずに（git は `git update-index --chmod=+x`）
