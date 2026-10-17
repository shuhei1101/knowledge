# Zustand — クロスルート state

Context で不十分なときに使う:
- 頻繁更新で Context だと全 consumer が re-render する
- React tree 外からも参照したい
- selector で部分購読したい

## ルール

- 配置: `app/(shared)/stores/use{Name}Store.ts`
- selector で部分購読（`useStore((s) => s.xxx)`）
- 永続化は `persist` ミドルウェア（`localStorage`）
- サーバーデータ / フォーム値は入れない
