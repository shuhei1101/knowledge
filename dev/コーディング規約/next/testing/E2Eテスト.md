# E2E テスト（Playwright）

## playwright.config.ts の要点

- `testDir: "./tests/e2e"`、`fullyParallel: true`、CI は `retries: 2` + `workers: 1`
- `trace: "on-first-retry"`、`screenshot: "only-on-failure"`
- projects に `storageState: "tests/e2e/.auth/user.json"` を設定（chromium / webkit / mobile）
- `webServer` で dev server 自動起動、`reuseExistingServer: !process.env.CI`

## フォルダ構成と責務

```
tests/
├── e2e/                        # spec のみ（画面・ドメイン単位フォルダ）
│   ├── auth/
│   │   └── login.spec.ts
│   ├── checkout/
│   │   └── apply-coupon.spec.ts
│   ├── usecases/               # 横断ユースケース
│   ├── .auth/                  # Storage State（gitignore 対象）
│   ├── reports/                # CI レポート出力先
│   ├── snapshots/              # visual regression 比較画像
│   ├── global.setup.ts         # Storage State 生成・DB 初期化
│   └── global.teardown.ts      # 後片付け
├── pages/                      # Page Object（UI 操作の抽象化のみ、業務ロジック禁止）
├── fixtures/                   # テストデータ Factory
└── helpers/                    # 共通操作。責務ごとに分割（helper.ts 乱立を避ける）
    ├── auth.ts
    ├── db.ts
    └── server.ts
```

## ルール

- ロケータは role / label / placeholder ベース。`data-testid` は最後の手段
- ログインは global.setup の Storage State で 1 回だけ（各 test で繰り返さない）。`.auth/` は gitignore
- DB シードは helpers で直接 insert（API 経由より高速・確実）
- DB 状態を共有するテストは `test.serial` で直列化
- CUJ（クリティカルパス）は必ず E2E でカバー
- 視覚回帰は `toHaveScreenshot`（`tests/e2e/snapshots/` に保存）
- a11y は `@axe-core/playwright` の AxeBuilder で violations ゼロを確認

## デバッグ

`--ui`（対話実行）/ `--debug`（DevTools）/ `show-trace`

## メイン dev server 起動中の E2E 実行

- Next.js は同一ディレクトリで dev server 1 つだけの制約があり、別ポートでも 2 つ目は起動エラーになる
- worktree（別ディレクトリ）に E2E 専用環境を作って実行する
  - worktree 作成 → `npm install` → `playwright install chromium`（初回のみ）→ 実行
  - E2E にはメインと被らない専用ポートを割り当てる
