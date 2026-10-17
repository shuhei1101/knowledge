# error.tsx / global-error.tsx

- `'use client'` 必須
- Props: `error: Error & { digest?: string }`, `reset: () => void`
- `useEffect` 内で `log.error`（`error.digest` でサーバーエラーと突合）
- ユーザーには汎用文言、詳細はログへ
- `reset()` で再 render ボタンを必ず設置
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
