# {タイトル}

{冒頭リード}

**ID**: {ID}

**公開範囲**: public / internal

**タグ**

<!-- table: {"kind": "data"} -->
| タグの名前 | 主題 |
| --- | --- |
| {タグの名前} | true / false |
<!-- /table -->

**別名**

- {別名}

**画面**: {画面}

**モック**: {モック}

<!-- table: {"kind": "plain", "collapse": {"open": false}} -->
| 対応テストファイル |
| --- |
| `{対応テストファイル}` |
<!-- /table -->

- {実装のファイル}

**画面の型**: list / detail / edit / settings / shell / other

**離脱の警告**: none / unsaved / autosave_error

<!-- table: {"kind": "data"} -->
| 保持するもの | 保持先 | キー | 保存する契機 | 戻す契機 | 優先する値 | 初期に戻す条件 | 理由 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| {保持するもの} | url_path / url_query / session_storage / local_storage / cookie / router / server / memory / none | {キー} | {保存する契機} | {戻す契機} | {優先する値} | {初期に戻す条件} | {理由} |
<!-- /table -->

## 要素一覧

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| 要素 | 項目 ID | 種類 | 部品 | 部品へ指定する引数 | スロットに差し込む中身 | 位置 | 固定の領域 | 説明 | 表示文言 | プレースホルダ | 入出力区分 | 型 | 表示条件 | 活性条件 | 必須 | 条件 | 要否の表示 | 制限 | 最小長 | 最大長 | 値の範囲・刻み | 形式 | 文字種の扱い | 表示幅 | 長い値の扱い | 件数の上限 | 表示形式 | 文字揃え | タブ順 | 初期フォーカス | 初期状態 | 応答を待つ間の状態 | アイコン | ラベルの出し方 | 読み上げ名 | ツールチップ | 狭い幅の出し方 | 押せない理由 | 取り消しの手段 | 結果の伝え方 | 切り替えの状態 | 読み上げの割り込み | 履歴の扱い | 一緒に戻す値 | ショートカット | 区画の配置 | タブ | 表の機能 | 並べ替え | 絞り込み | 固定 | 非表示 | 閉じ方 | 後ろの操作を止める | 開いたときのフォーカス | 閉じた後のフォーカス | 保持する状態 | 初期値 | 補助文 | 入力の目的 | 入力モード | 接頭辞 | 接尾辞 | 選択肢 | 入力例 | 取得元 | 送信先 | アクション | アクションの参照 | 関連 | 検討事項 | 理由 | 状態 | 公開 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {要素} | {項目 ID} | button / link / toggle / input / textarea / select / checkbox / radio / tabs / nav / sidebar / pane / splitter / drag_handle / disclosure / list / tree / board / table / table_column / dialog / popover / tooltip / heading / label / image / alert / toast / progress / separator / shortcut | {部品} | name: {引数}、value: {指定する値} | name: {スロット}、value: {差し込む中身} | {位置} | true / false | {説明} | {表示文言} | {プレースホルダ} | input / output / input_output | {型} | {表示条件} | {活性条件} | true / false | {条件} | {要否の表示} | {制限} | {最小長} | {最大長} | min: {最小}、max: {最大}、step: {刻み} | {形式} | {文字種の扱い} | {表示幅} | type: wrap / truncate / scroll、max_length: {表示する最大の長さ}、unbounded: true / false | max_count: {表示する最大の件数}、type: wrap / summarize / paginate | {表示形式} | left / center / right | {タブ順} | true / false | enabled / disabled / readonly | {応答を待つ間の状態} | {アイコン} | icon_only / icon_and_text / text_only | {読み上げ名} | {ツールチップ} | action: hidden / icon_only / short_label / into_menu / stack / horizontal_scroll / collapse_column / drawer、short_label: {短い文言}、priority: {残す順} | {押せない理由} | dialog / undo / none | success: {成功}、failure: {失敗} | pressed / expanded / checked | polite / assertive | push / replace | {一緒に戻す値} | key: {キー}、scope: app / screen / pane / dialog | side: left / right / top / bottom、width: {'default': '{既定}', 'min': '{最小}', 'max': '{最大}'}、resizable: true / false、collapsible: true / false、default_collapsed: true / false、narrow: drawer / bottom_sheet / stack_below / separate_screen / hidden、focus_on_open: {開いたときのフォーカス} | items: [{'label': '{見出し}', 'value': '{値}', 'count_source': '{件数の取得元}'}]、mode: in_screen / navigation、activation: automatic / manual、empty_behavior: {中身が無いときの扱い} | default_sort: {既定の並び}、filter: {絞り込み}、column_visibility: true / false、sticky_header: true / false、row_click: {行を押したとき}、row_link: {行のリンク先}、selection: none / single / multiple、bulk_actions: {一括操作}、copy: {コピー}、grid_navigation: true / false | true / false | true / false | true / false | true / false | outside_click: true / false、escape: close / confirm / none | true / false | {開いたときのフォーカス} | {閉じた後のフォーカス} | what: {保持するもの}、store: url_path / url_query / session_storage / local_storage / cookie / router / server / memory / none、key: {キー}、save_on: {保存する契機}、restore_on: {戻す契機}、precedence: {優先する値}、reset_when: {初期に戻す条件}、reason: {理由} | {初期値} | {補助文} | {入力の目的} | {入力モード} | {接頭辞} | {接尾辞} | {選択肢} | {入力例} | {取得元} | {送信先} | {アクション} | {アクションの参照} | to: {相手の ID}、item: {項目のパス}、type: requires / references / replaces / part_of / change_together、when: {いつ参照するか}、paths: ['{対象のパス}'] | {検討事項} | {理由} | planned / implemented / deprecated / removed | user / developer |
<!-- /table -->

## 入力チェック

<!-- table: {"kind": "data"} -->
| 要素 | 違反の条件 | 検証の契機 | エラー文言 | 表示位置 |
| --- | --- | --- | --- | --- |
| {要素} | {違反の条件} | {検証の契機} | {エラー文言} | {表示位置} |
<!-- /table -->

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 項目のパス | 関係の種類 | いつ参照するか | 対象のパス |
| --- | --- | --- | --- | --- |
| {相手の ID} | {項目のパス} | requires / references / replaces / part_of / change_together | {いつ参照するか} | {対象のパス} |
<!-- /table -->

**検討事項**

- {検討事項}
