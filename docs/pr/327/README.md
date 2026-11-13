# プラグイン knowledge とプラグイン slop-check の配置を統一する

## 概要

プラグイン knowledge とプラグイン slop-check を、同じ決まりのフォルダに配置する。

## 背景

[Issue #278](https://github.com/shuhei1101/knowledge/issues/278) の要望。
フォルダ構成の設計書 [LAY-72-1](https://github.com/shuhei1101/knowledge/blob/develop/docs/layout/LAY-72-1.yaml) を規約『フォルダ構成の切り方とレビュー』の「同じ種類が散る」の観点で確認した結果（[#220](https://github.com/shuhei1101/knowledge/issues/220)・[#274](https://github.com/shuhei1101/knowledge/issues/274)）、同じ役割（`plugin_manifest`・`skill`）のファイルが、プラグイン knowledge は直下の `.claude-plugin/plugin.json`・`skills/`、プラグイン slop-check は `plugins/slop-check/` の下に分かれている。
直下の `.claude-plugin/` には、プラグイン knowledge の定義とマーケットプレイスの定義が同居している。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
