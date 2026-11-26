# 動画

動画作成で作る動画 1 本。セグメントの一覧と、成果物ごとのバージョンと利用者の OK を持つ。

**ID**: DATA-1

**保存先**: SQLite

## キー

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| キー | 論理名 | 型 | 必須 | 説明 | 例 | 一意の範囲 | 参照先 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | 動画 ID | string | ✓ | 動画 1 本の識別子 |  | 全体 |  |
| script_id | 台本 ID | ref |  | 元にした台本。台本を削除すると空になる |  | 値があるものの中 | DATA-2#fields[id] |
| segments[] | セグメント | array |  | この動画のセグメントの一覧。配列の順が、動画の中の順 |  |  |  |
| segments[].segment_id | セグメント ID | ref | ✓ | 中身を持つセグメント |  | 全体 | DATA-3#fields[id] |
| segments[].artifacts[] | 成果物 | array |  | セグメントの成果物ごとのバージョンと OK |  |  |  |
| segments[].artifacts[].kind | 種類 | enum | ✓ | `lines`（セリフ）/ `direction`（演出）/ `video`（セグメントの mp4） | lines | セグメントの中 |  |
| segments[].artifacts[].version | バージョン | int | ✓ | 1 から始まり、再作成するたびに 1 増える | 2 |  |  |
| segments[].artifacts[].state | 状態 | enum | ✓ | `current`（最新）/ `stale`（要更新） | current |  |  |
| finished_at | 完成日時 | datetime |  | 最後に完成にした時刻 |  |  |  |
<!-- /table -->

## 複合の鍵

<!-- table: {"kind": "data"} -->
| キー | 条件 | 使用するインターフェース |
| --- | --- | --- |
| script_id | `script_id` がある | 動画作成を始める操作 |
<!-- /table -->

## 状態の遷移

### segments[].artifacts[].state

<!-- table: {"kind": "data"} -->
| 元の値 | 先の値 | きっかけ |
| --- | --- | --- |
| （なし） | current | 成果物を書き込んだ |
| current | stale | 上流の成果物のバージョンが増えた |
<!-- /table -->

## 保持と削除

<!-- table: {"kind": "data"} -->
| キー | 増え方 | 保持期間 | 削除の方針 |
| --- | --- | --- | --- |
| （全体） | 動画作成を始めるたびに 1 件。～1000 | 無期限 | 制作の削除で、セグメントと一緒に削除する |
| segments[] | 動画 1 本に 5〜20 件 | 動画と同じ | 切り方で引き継がなかったセグメントは、利用者が切り方を OK にしたときに削除する |
<!-- /table -->

## 参照・更新するインターフェース

<!-- table: {"kind": "data"} -->
| インターフェース | 参照・更新 | キー |
| --- | --- | --- |
| 動画作成を始める | write | id・script_id |
| 動画の取得 | read | id・segments[]・finished_at |
<!-- /table -->
