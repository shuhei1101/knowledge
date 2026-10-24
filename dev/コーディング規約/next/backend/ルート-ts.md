# app/api/v{N}/{resource}/route.ts

HTTP ハンドラ（GET / POST / PATCH / DELETE）。`withRouteErrorHandling` でラップし、認証 → Zod パース → `service.ts` 呼び出しの順に書く。
## ルール

- すべての handler を `withRouteErrorHandling` でラップ（try/catch は書かない）
- 認証必須なら `getAuthContext()` を最初に呼ぶ
- リクエストボディ・クエリは Zod で `.parse`（投げると 400）
- レスポンス封筒: `{ data, meta? }` / `{ error: { code, message, field? } }`
- 成功 (mutation) は `204 No Content` を返す（body なし）
- HTTP メソッド: 新規 = POST、部分更新 = PATCH、全置換 = PUT、削除 = DELETE
- 件数が増えうる一覧は最初からページに分け、次のページを取る手がかり（URL か cursor）を返す
- 時間のかかる処理は、受け付けた時点で 202 と状態を照会する先を返し、完了まで待たせない
