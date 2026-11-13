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
| 文書の検査の CI | `docs-check.yml` と IF-72-4 を削除し、SC-72-6 を開発者がクローンで全ての文書の検査のコマンドを実行する流れにする。ARCH-72-1・LAY-72-1・NFR-72-1・CMD-72-1 の CI での検査の記述を削除する | 全ての文書の検査（IF-72-3）は lint に当たり、Git フックと CI で動かすのは生成・配布だけにするため |

## 設計書の確定コミット

| 工程 | 範囲 | 補足 |
| --- | --- | --- |
| 単一ユースケース設計 | `fa2dd73..9067838` | SC-137-1・SC-72-6 |
| 単一ユースケース設計 | `1dda2d4..01ee957` | レビューの指摘の修正 |
| インターフェース定義設計 | `0b306f0..4108cf3` | IF-137-2 の変更・IF-72-4 の削除と、IF-72-4 を指す LAY-72-1 の行 |

## テスト結果

なし
