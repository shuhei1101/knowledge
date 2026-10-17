# drizzle/schema.ts — Enum

- 固定セットの値を取るカラムは `pgEnum` で型安全に定義。
- 値が動的に変わる（ユーザー追加可能等）なら別テーブルで管理
- 値は削除できない（Postgres は追加と改名のみ）。削除は『DBマイグレーション』の手順で型を作り直す
- カラム JSDoc に値の説明を付ける


## テンプレ

```ts
import { pgEnum } from "drizzle-orm/pg-core"

/** リソースステータス */
export const resourceStatus = pgEnum("resource_status", [
  "draft",       // 下書き
  "published",   // 公開中
  "archived",    // アーカイブ
])
export type ResourceStatus = (typeof resourceStatus.enumValues)[number]
```

## Zod スキーマと併用

```ts
import { z } from "zod"

export const ResourceFormSchema = z.object({
  status: z.enum(resourceStatus.enumValues),
})
```

## 命名

| 対象                                 | 命名                                             |
| ------------------------------------ | ------------------------------------------------ |
| Enum 定義（camelCase 単数）          | `resourceStatus`, `userType`, `notificationType` |
| Postgres での名前（snake_case 単数） | `resource_status`, `user_type`                   |
| TypeScript の型（PascalCase 単数）   | `ResourceStatus`, `UserType`                     |

`*Enum` 接尾辞は付けない
