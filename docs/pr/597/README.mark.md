# 規約『Claude 成果物の共通ルール』に、認証情報をコピーして Claude Code を起動しない決まりと確認の起動の方法を記載する

## 概要

Claude Code を動作確認のために起動する人が、本番の認証領域をログアウトさせずに、認証が要る確認と要らない確認の起動の方法を規約から選べるようにする。

## 背景

[Issue #595](https://github.com/shuhei1101/knowledge/issues/595) の要望。
本番の認証領域（`~/.claude*`）の `.credentials.json` を別の場所へコピーして `claude` を起動すると、コピーした先で token が取り直され、元の認証領域がログアウトする。
ai-monitor では暫定として連絡ボードに起動の方法を記載している（2026-10-02 ユーザー判断）。
[shuhei1101/ai-monitor#3851](https://github.com/shuhei1101/ai-monitor/pull/3851) で扱う [shuhei1101/ai-monitor#2364](https://github.com/shuhei1101/ai-monitor/issues/2364) で、AI とツールに依らない決まりを ai-monitor の規約『実行環境の認証情報』へ、Claude Code の具体を knowledge の Claude の規約へ記載すると決めた。shuhei1101/ai-monitor#3851 はこの PR を待っている。
規約『Claude 成果物の共通ルール』（`claude-common`）を含む `claude-*` の規約に、認証情報のコピーと確認の起動の方法の記述は無い。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
