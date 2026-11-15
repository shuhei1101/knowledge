# リポジトリを Windows のドライブ（/mnt/c）と Linux 側のどちらに配置するかの判定フローチャートを追加する

## 概要

WSL で開発する人が、新規のリポジトリでも既存のリポジトリでも、リポジトリを Windows のドライブ（`/mnt/c`）と Linux 側（ext4）のどちらに配置するかを、knowledge の判定フローチャートで決められるようにする。

## 背景

[Issue #423](https://github.com/shuhei1101/knowledge/issues/423) の要望。
全てのリポジトリを `/mnt/c` に配置した結果、ファイルの読み書きのたびに WSL と Windows の間の 9P の通信を待ち、venv の import の遅れ（[ai-monitor#3350](https://github.com/shuhei1101/ai-monitor/issues/3350)）・worktree の作成と削除の上限超過・常駐のプロセスの周期の詰まり（[ai-monitor#3511](https://github.com/shuhei1101/ai-monitor/issues/3511)）が起きている。
一方で、Windows の上で動かすものを持つリポジトリは、Linux 側に配置すると Windows 側から `\\wsl.localhost\...` 経由で参照することになる。
[ai-monitor#3512](https://github.com/shuhei1101/ai-monitor/issues/3512)（監視対象と AI Monitor 自身を Linux 側へ移す）はこの判定フローチャートに依存し、監視対象を加える手順・リポジトリを新規作成する手順から参照する。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
