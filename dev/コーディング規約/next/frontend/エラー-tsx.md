# error.tsx / global-error.tsx

- `'use client'` 必須
- Props: `error: unknown`（`instanceof Error` で絞ってから `digest` を読む）, `retry: () => void`
- `useEffect` 内で `log.error`（`error.digest` でサーバーエラーと突合）
- ユーザーには汎用文言、詳細はログへ
- `retry()` で再取得・再 render するボタンを必ず設置（`reset()` は再取得しない）
- `global-error.tsx` は `<html><body>` を自前で書く（ルート layout 自体が落ちる前提）

## 配置

```
app/
├── global-error.tsx          # ルート layout 自体のエラー
├── error.tsx                 # ルート layout 配下
└── (authenticated)/
    ├── error.tsx             # 認証エリア全体
    └── resources/
        └── error.tsx         # resources 配下
```
