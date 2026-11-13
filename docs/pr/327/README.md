# プラグイン knowledge だけを直下に配置する理由をフォルダ構成の設計書に記載する

## 概要

プラグインの配置の決まり（knowledge だけを直下に配置し、他は `plugins/{plugin}/` に配置する）とその理由を、フォルダ構成の設計書で参照できるようにする。

## 背景

[Issue #278](https://github.com/shuhei1101/knowledge/issues/278) の要望。
フォルダ構成の設計書 [LAY-72-1](https://github.com/shuhei1101/knowledge/blob/develop/docs/layout/LAY-72-1.yaml) を規約『フォルダ構成の切り方とレビュー』の「同じ種類が散る」の観点で確認した結果（[#220](https://github.com/shuhei1101/knowledge/issues/220)・[#274](https://github.com/shuhei1101/knowledge/issues/274)）、同じ役割（`plugin_manifest`・`skill`）のファイルが、プラグイン knowledge は直下の `.claude-plugin/plugin.json`・`skills/`、プラグイン slop-check は `plugins/slop-check/` の下に分かれている。
直下の `.claude-plugin/` には、プラグイン knowledge の定義とマーケットプレイスの定義が同居している。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
