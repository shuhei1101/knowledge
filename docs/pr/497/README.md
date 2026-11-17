# 部品設計・画面設計・シナリオの test_file に、規約『フォルダ構成』の React の結合テストと E2E のファイルを記載できるようにする

## 概要

部品設計・画面設計の `test_file` に規約『フォルダ構成』のとおり対象の横に配置した React の結合テストのファイルを、シナリオの `test_file` に `frontend/tests/e2e/` に配置した E2E のファイルを記載できるようにする。

## 背景

[Issue #496](https://github.com/shuhei1101/knowledge/issues/496) の要望で、[Issue #495](https://github.com/shuhei1101/knowledge/issues/495) と [Issue #494](https://github.com/shuhei1101/knowledge/issues/494) の束。
develop の `schemas/design/component.schema.yaml`・`screen.schema.yaml`・`scenario.schema.yaml` の `test_file` は `pattern: ^tests/.+` で、テストのファイルを `tests/` の下に限っている。
規約『フォルダ構成』（`react-core-folder-structure`）は、unit・結合テストと stories を対象の横（`test-01`）、E2E を `frontend/tests/e2e/`（`test-02`）に配置すると定めている。
同じ食い違いのモジュール構成の `test_files` は [PR #493](https://github.com/shuhei1101/knowledge/pull/493) で直しており、部品設計・画面設計・シナリオは #493 のスコープ外として切り出した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
