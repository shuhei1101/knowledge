# tsc 運用（バニラ TS + FastAPI）

- ブラウザに出すのは `tsc` が生成した `.js`。
  - バンドラは使わない（`html/core/ビルドレス原則.md`）。
  - `.ts` を著作し、`tsc` がトランスパイル 1 段だけ挟む。
- 生成 `.js` は `.ts` と同じ階層に出す。`screen.ts` → 同じフォルダに `screen.js`。
- 以下の `frontend/` は画面のスクリプトの置き場所を指す。`static/`・`assets/` などに置く構成では、そのフォルダに読み替える。

## 設定ファイル（repo ルート）

<!-- table: data -->

| ファイル              | 役割                                                                                              |
| --------------------- | ------------------------------------------------------------------------------------------------- |
| `tsconfig.json`       | 型チェック用。`noEmit`。`frontend/**/*.ts`（移行期は `.js` も）を include                         |
| `tsconfig.build.json` | 生成用。`tsconfig.json` を継承し `noEmit:false` + 同階層 emit。include は `frontend/**/*.ts` のみ |
| `tsconfig.plan.json` | 型チェック用。トップレベルの宣言が重なる従来のスクリプト（`import` / `export` の無い `.ts`）を、`tsconfig.json` と別のプログラムにする。`tsconfig.json` を継承し include だけを変える |
| `tsconfig.plan.build.json` | 生成用。`tsconfig.plan.json` を継承し、`tsconfig.build.json` と同じ形で出す |
| `eslint.config.mjs`   | flat config。`typescript-eslint` で `.ts` を lint。Next/React 設定は使わない。`@typescript-eslint/no-deprecated` を有効にし、型情報つきの設定（`parserOptions.projectService`）で動かす |
| `package.json`        | dev ツールの devDependencies と scripts（`type: module`）                                         |

<!-- /table -->

importmap の別名（`shared/`）は `tsconfig.json` の `paths` で `./frontend/shared/*` に解決する。

## scripts

<!-- table: data -->

| script      | 中身                                 | 用途                                                     |
| ----------- | ------------------------------------ | -------------------------------------------------------- |
| `dev`       | `tsc -p tsconfig.build.json --watch` | 開発中。保存ごとに変更分だけ再生成（数百 ms）            |
| `build`     | `tsc -p tsconfig.build.json`         | 全 `.ts` を一括生成                                      |
| `typecheck` | `tsc -p tsconfig.json --noEmit`      | CI / pre-commit。型崩れ検知                              |
| `lint`      | `eslint frontend`                    | flat config                                              |
| `test`      | `vitest run` / `playwright test`     | テスト                                                   |
| `gen-types` | `openapi-typescript`                 | API 型を `shared/api/schema.d.ts` に生成（コミットする） |

<!-- /table -->

## 生成 .js は gitignore

著作は `.ts`、`.js` は生成物。フロントエンドの生成 `.js` はコミットしない（`.gitignore`）。例外は手書きで維持する `shared/vendor/`（外部依存の vendoring）と openapi 生成型 `shared/api/schema.d.ts`（コミットする）。
ビルドしない配信先（GitHub Pages・配布先）と共用する生成 `.js` と、配信・テスト・Storybook・モックの配信がビルドせずにパスを直接読む生成 `.js` は、`.ts` と同じ階層へコミットする。
コミットする生成 `.js` はプロジェクトの設計書に列挙し、列挙したものに限る。
