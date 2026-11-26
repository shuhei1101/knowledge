# aituber

機能ごとのフォルダと、コードではない原本の `content/` に分ける。

**ID**: LAY-1

**リポジトリ**: shuhei1101/aituber

## 中身の種類

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| 種類 | 分類 | 説明 |
| --- | --- | --- |
| agent_flow | role | エージェントが参照するエージェントフロー |
| config | role | 設定ファイル |
| brain | feature | ブレインノード |
<!-- /table -->

## エントリ

### src

**種別**: folder

**配置するもの**: コード（src レイアウトのため、パッケージ 1 つだけを配置する）

**配下のエントリ**

<!-- table: {"kind": "data"} -->
| type | name | contents | convention | children |
| --- | --- | --- | --- | --- |
| folder | aituber | サーバー本体のコード | python-architecture-layout | type: file、name: flow_schema.py、contents: エージェントフローのスキーマから生成した型、generated_from: {'path': 'content/node-docs/schema.yaml', 'command': 'CMD-1#categories[ビルド・生成]', 'tracked': '実行時に import する'} |
<!-- /table -->

### content

**種別**: folder

**配置するもの**: コードではない原本

**配下のエントリ**

<!-- table: {"kind": "data"} -->
| type | name | contents | id_root | children |
| --- | --- | --- | --- | --- |
| folder | node-docs | ノードのエージェントフローと、そのスキーマ | ✓ | type: file、name: schema.yaml、contents: エージェントフローのスキーマ<br>type: folder、name: shared、contents: 複数のノードが埋め込む手順の部品、content_types: ['agent_flow']、naming: ['{part}.yaml']、used_by: ['AG-1#', 'AG-2#']<br>type: folder、name: brain、contents: 活動ごとのブレインノードの手順、children: [{'type': 'folder', 'name': 'stream', 'contents': '配信のブレインノードの手順', 'content_types': ['agent_flow', 'brain'], 'naming': ['{stage}.yaml'], 'placeholders': [{'name': 'stage', 'from': 'AG-1#stages'}], 'used_by': ['AG-1#']}, {'type': 'folder', 'name': 'chat', 'contents': '雑談のブレインノードの手順', 'content_types': ['agent_flow', 'brain'], 'naming': ['{stage}.yaml'], 'placeholders': [{'name': 'stage', 'from': 'AG-2#stages'}], 'used_by': ['AG-2#']}] |
<!-- /table -->

### dist

**種別**: folder

**配置するもの**: ビルドしたフロントエンド

**生成元**

**生成元のパス**: frontend/

**生成するコマンド**: CMD-1#categories[ビルド・生成]

## Git で管理しないもの

<!-- table: {"kind": "data"} -->
| パターン | 理由 |
| --- | --- |
| dist/ | 生成物 |
| tmp/ | 一時ファイル |
<!-- /table -->

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 関係の種類 | いつ参照するか |
| --- | --- | --- |
| ARCH-1 | references | サブシステムのフォルダを追加・移動するときに、アーキテクチャ図のサブシステムの分け方を確認する。 |
<!-- /table -->
