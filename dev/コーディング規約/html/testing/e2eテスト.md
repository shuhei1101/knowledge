# E2E テスト（playwright）

- スペックは `frontend/tests/e2e/{name}.spec.ts`。`import { test, expect } from "@playwright/test"`。
- 外部 I/O（LLM / TTS 等）は `playwright.config.js` の webServer env に渡す環境変数でモックに切り替える。
  - 実課金・非決定性に依存させない。
- ロケータは role / text / label ベースを優先。
  - 画面の `id` で参照するのは実装と対応が明確な範囲に留め、`data-testid` は最後の手段。
- (FastAPI使用時)実 FastAPI とファイル永続を共有するため直列実行（`workers: 1`・`fullyParallel: false`）。
- 検証対象は「画面が組み上がる・共通シェルが付く・主要操作とバリデーション」。
  - ユニットで足りることは持ち込まない。
- メイン dev server 稼働中に走らせるときは worktree から別ポート（`E2E_PORT`）で起動する。
  - 設定詳細は `playwright.config.js`（worktree の src を PYTHONPATH に、メインリポジトリの venv / settings を参照）。
