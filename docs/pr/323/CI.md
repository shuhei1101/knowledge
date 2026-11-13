# CI

## 現状

| 分類 | ページ / ファイル | 概要 | 補足 |
| --- | --- | --- | --- |
| ドキュメント | [docs/scenario/SC-137-1.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/scenario/SC-137-1.yaml) | 利用者が GitHub Pages で knowledge の公開文書を読む | master へのマージで配信する。更新対象 |
| ドキュメント | [docs/interface/IF-137-2.yml.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/interface/IF-137-2.yml.yaml) | 公開文書の配信のワークフロー | `master` への `push` で起動する。更新対象 |
| ドキュメント | [docs/scenario/SC-72-6.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/scenario/SC-72-6.yaml) | 開発者が文書の違反を検査する | CI で全ての文書を検査する。更新対象 |
| ドキュメント | [docs/interface/IF-72-4.yml.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/interface/IF-72-4.yml.yaml) | 文書の検査のワークフロー | `develop`・`master` への push と PR で起動する。更新対象 |
| ドキュメント | [docs/architecture/ARCH-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/architecture/ARCH-72-1.yaml) | アーキテクチャ図 | サブシステム CI の役割と「master への push」の矢印。更新対象 |
| ドキュメント | [docs/layout/LAY-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/layout/LAY-72-1.yaml) | フォルダ構成 | `docs-check.yml`・`pages.yml` の行。更新対象 |
| ドキュメント | [docs/nonfunctional/NFR-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/nonfunctional/NFR-72-1.yaml) | 非機能要件 | CI の 1 回の所要時間。`docs-check.yml` を削除する場合は更新対象 |
| ドキュメント | [docs/dev-command/CMD-72-1.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/dev-command/CMD-72-1.yaml) | 開発コマンド | maid のバージョンを上げるときに `docs-check.yml` も直す手順。`docs-check.yml` を削除する場合は更新対象 |
| 実装 | [.github/workflows/pages.yml](https://github.com/shuhei1101/knowledge/blob/develop/.github/workflows/pages.yml) | GitHub Pages への配信 | `push: branches: [master]` を develop にする |
| 実装 | [.github/workflows/docs-check.yml](https://github.com/shuhei1101/knowledge/blob/develop/.github/workflows/docs-check.yml) | 全ての文書の検査 | 新しい決まりに合わせて見直す |

## 変更方針

| 対象 | 方針 | 補足 |
| --- | --- | --- |
| 公開文書の配信 | `pages.yml` の起動を `develop` への `push` と `workflow_dispatch` にし、SC-137-1・IF-137-2・ARCH-72-1・LAY-72-1 の master を develop に直す | GitHub Pages の環境 `github-pages` の配信を許すブランチに develop を足す（反映作業） |
| 文書の検査の CI | `docs-check.yml` と、それを前提にした SC-72-6・IF-72-4・ARCH-72-1・LAY-72-1・NFR-72-1・CMD-72-1 の記述を削除する | `未確定`（決める段: 単一ユースケース設計） |

| 案 | 内容 |
| --- | --- |
| A | `docs-check.yml` と対応する設計書を削除し、文書の検査は dev-docs の validator とエージェントの手順で回す |
| B | `docs-check.yml` を残す |

推奨: A

全ての文書の検査は lint に当たり、動かしてよい生成・配布に当たらないため。

## テスト結果

なし
