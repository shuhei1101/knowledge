# bat ランチャー

Windows で Python スクリプトを起動する `.bat` の規約。

## 標準テンプレート

```bat
@echo off
chcp 65001 > nul
setlocal

:: cd into this script's directory
cd /d "%~dp0"

:: activate venv if present
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

:: timestamp via PowerShell (locale-independent)
for /f "delims=" %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set TS=%%i

if not exist log mkdir log
set LOG=log\script-%TS%.log

python script.py %* > "%LOG%" 2>&1
set EXIT_CODE=%ERRORLEVEL%

type "%LOG%"
echo.
echo (log: %LOG%)
echo (exit: %EXIT_CODE%)

endlocal & exit /b %EXIT_CODE%
```

## 必須要素

<!-- table: data -->

| 要素                             | 理由                                                 |
| -------------------------------- | ---------------------------------------------------- |
| `@echo off` + `chcp 65001 > nul` | コマンド非表示 + UTF-8 化                            |
| `setlocal` 〜 `endlocal`         | 環境変数の汚染防止                                   |
| `cd /d "%~dp0"`                  | bat の場所を基準に                                   |
| venv の存在チェック付き activate | 自動有効化                                           |
| PowerShell でタイムスタンプ      | `%date%` `%time%` は locale 依存で形式が変わり事故る |
| `%*`                             | 全引数を Python へ転送（argparse がそのまま解釈）    |
| `> "%LOG%" 2>&1` + `type`        | ログ保存 + 画面表示                                  |
| `exit /b %EXIT_CODE%`            | Python の終了コードを呼び出し元へ                    |

<!-- /table -->

## bat 内に日本語を書かない

文字列・コメントとも ASCII / 英語のみ。日本語表示が必要なら bat は呼ぶだけにして Python 側で出力する。sh ランチャー（UTF-8 標準）は日本語可。
