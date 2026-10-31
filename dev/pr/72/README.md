# knowledge を dev-docs の配信元として使えるようにし、使い方を書き直す

## 概要

利用者が `/dev-docs:setup` で knowledge を dev-docs の配信元に登録すると、どの端末・プロジェクトからでも規約を画面で読み、dev-docs の MCP に `source: knowledge` を渡して検索・取得できるようになる。

## 背景

[Issue #51](https://github.com/shuhei1101/knowledge/issues/51) の要望。
今は clone して `RULE_INJECT_INDEXES_USER` に `rules.yaml` を書くだけで使い、knowledge のプラグイン・MCP・開発ドキュメントサーバーは無い。
[#64](https://github.com/shuhei1101/knowledge/pull/64)（[#44](https://github.com/shuhei1101/knowledge/issues/44)）で文書を YAML に移した後も、タグやメタデータで規約を引く手段が無い。
スキーマ・参照の検査と CI は、#64 のレビューでこの Issue に含めると決まった（[コメント](https://github.com/shuhei1101/knowledge/pull/64#discussion_r4367269018)）。
開発ドキュメントサーバーと文書の MCP は各リポジトリが作らず、汎用の dev-docs を使うと決まった（[ユーザーの追記](https://github.com/shuhei1101/knowledge/issues/51#issuecomment-6386949622)、D-96〜D-115）。
dev-docs の本体は [shuhei1101/dev-docs#3](https://github.com/shuhei1101/dev-docs/issues/3)・[shuhei1101/dev-docs#4](https://github.com/shuhei1101/dev-docs/issues/4)、規約は [#73](https://github.com/shuhei1101/knowledge/issues/73) が受け持つ。
#73 の規約の改訂で、各リポジトリは文書の MCP のプラグインとマーケットプレイスを持たないと決まり、[#76](https://github.com/shuhei1101/knowledge/issues/76) をこの Issue に統合した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [反映作業](./反映作業/index.yaml) | この端末の dev-docs への knowledge の登録 |

対象システムごとの計画書は、初期構築でアーキテクチャ図のサブシステムを決めた後に追加する。

## タスク一覧

- [x] 初期構築（アーキテクチャ図・非機能要件・設計書の置き場所。コードを持つのはこの PR が初めて）
- [x] ~~リバースエンジニアリング~~（設計書も実装も無く、起こす対象が無い）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [x] PoC 検証（検査のスクリプトが呼ぶ `@probelabs/maid` の `--fix` 無しの検査の出力と終了コード）
- [x] 複合ユースケース設計
- [x] ~~デザインスタイル選定~~（画面は dev-docs が持ち、mdmark の共通スタイルで描く（D-85・D-96））
- [x] ~~画面一覧・画面遷移~~（画面と画面遷移は dev-docs が持ち、knowledge は `nav` でタブとサイドバーの並びを書くだけ）
- [x] 単一ユースケース設計
- [x] ~~モック作成~~（画面は dev-docs が持ち、knowledge は画面を作らない）
- [x] インターフェース定義設計
- [x] ~~部品設計~~（画面の部品は dev-docs と mdmark が持つ）
- [x] ~~画面設計~~（画面の UI 項目は dev-docs が持ち、knowledge の変更は画面の UI 項目を増やさない）
- [ ] モジュール構成設計
- [ ] ドキュメント修正（要件.md の `## 更新ドキュメント`）
- [ ] 単体テスト作成
- [ ] 実装
- [ ] 結合テスト作成
- [ ] E2E テスト作成

## PoC 結果

結論: 成立（[PoC PR #133](https://github.com/shuhei1101/knowledge/pull/133)、commit 8d7b885）。
ただし maid は Linux 側のファイルシステムに入れて PATH から呼ぶ。`/mnt/c` の作業ツリーの `node_modules` に入れると、1 回の起動に 9〜14 秒かかり、図が複数ある文書は 20 秒を超える。

| 観点 | 基準 | 結果 |
| --- | --- | --- |
| 正しい図 | develop の mermaid を含む全文書で終了コード 0 | 13 文書すべて 0（4 つ以上のバッククォートで囲んだ記述例の中の図は検査から外す） |
| 誤った図 | 壊した 3 種の全てで 0 以外 | 3 種すべて 1 |
| 出力 | 誤りの行番号と内容を機械で取り出せる | `--format json` の `errors[]` の `line`・`column`・`message` で取れる。`code` は誤りの種類によって無い |
| 行の対応づけ | 文書の項目と行に戻せる | `yaml.compose` の項目の開始行＋ブロックの開始行＋maid の `line` で、項目のパスと文書の行に戻せた（閉じ忘れは閉じのフェンスの行になる） |
| 書き換えない | 前後でハッシュが変わらない | 16 ファイルすべて一致 |
| 処理時間 | インストール済みで 20 秒以内 | Linux 側に入れた maid で最大 0.90 秒（`template-scenario.yaml`）。`/mnt/c` に入れた maid では 16 件中 6 件が 20 秒で時間切れ（[結果](https://github.com/shuhei1101/knowledge/blob/8d7b885/poc/maid/result-mntc.tsv)） |
| 起動時の確認 | `maid` が PATH から引けないときを見分ける | `shutil.which` で検査の前に見分け、終了コード 2 と標準エラーの JSON で返した |

所感:

- 標準入力（`maid - --format json`）で渡せるので、一時ファイルは要らない
- 残り時間で maid を打ち切ったときの `TimeoutExpired` を捕まえず、スクリプトが落ちた。本実装では時間切れを違反として返す
- 開発コマンドの環境構築に、maid を Linux 側へ入れる手順（`npm install -g` など）を書く

要点（[check_mermaid.py](https://github.com/shuhei1101/knowledge/blob/8d7b885/poc/maid/check_mermaid.py)）:

```python
def blocks(node, path=""):
    if isinstance(node, yaml.MappingNode):
        for k, v in node.value:
            yield from blocks(v, f"{path}.{k.value}" if path else k.value)
    elif isinstance(node, yaml.SequenceNode):
        for i, v in enumerate(node.value):
            yield from blocks(v, f"{path}[{i}]")
    elif isinstance(node, yaml.ScalarNode) and "```mermaid" in str(node.value):
        base = node.start_mark.line + (1 if node.style in ("|", ">") else 0)
        ...  # 4 つ以上のバッククォートの囲みを飛ばし、```mermaid のブロックを (項目, base + 開始行 + 1, 本文) で返す

res = subprocess.run([maid, "-", "--format", "json"], input=body, capture_output=True, text=True, timeout=left)
for e in json.loads(res.stdout).get("errors", []):
    violations.append({"item": item, "line": doc_line + e["line"] - 1, "column": e["column"], "code": e.get("code"), "message": e["message"]})
```

PoC PR の見どころは、`check_mermaid.py`（取り出しと行の対応づけ）・`run_like_devdocs.py`（dev-docs の `run_script` と同じ約束で 30 秒で打ち切って呼ぶ）・`fixtures/ng/`（壊した 3 種）。
