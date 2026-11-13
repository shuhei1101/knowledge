# module

物理ファイルごとの関数・型・定数と、分類の構成図

## 目次

<!-- table: data -->

| ページ | 概要 |
| --- | --- |
| [slop-check / hooks / slop_check.py](./MOD-148-2.py.yaml) | プラグイン slop-check の PostToolUse のフック。書き込んだ中身を対応表のコピーで照合し、ヒットした行の通知の文を `additionalContext` で返却する（IF-148-1）。 |
| [検査と変換のスクリプト / scripts / _common.py](./MOD-72-2.py.yaml) | 文書の読み込み・項目のパスと行の対応・違反の型・並列の読み込み |
| [検査と変換のスクリプト / scripts / _lint.py](./MOD-176-1.py.yaml) | markdownlint-cli2・textlint・yamllint の在りかの確認と呼び出しと違反の行の対応 |
| [検査と変換のスクリプト / scripts / _maid.py](./MOD-72-3.py.yaml) | maid の在りかの確認と打ち切りつきの呼び出し |
| [検査と変換のスクリプト / scripts / build_pages.py](./MOD-137-1.py.yaml) | CI と手元から呼ぶ Pages の成果物の作成 |
| [検査と変換のスクリプト / scripts / build_templates.py](./MOD-201-1.py.yaml) | 手元から呼ぶ設計書のテンプレートの生成 |
| [検査と変換のスクリプト / scripts / build_word_list.py](./MOD-148-3.py.yaml) | 手元から呼ぶ対応表のコピーの作成 |
| [検査と変換のスクリプト / scripts / check_all.py](./MOD-72-6.py.yaml) | CI と手元から呼ぶ全ての文書の検査 |
| [検査と変換のスクリプト / scripts / knowledge_checks.py](./MOD-72-4.py.yaml) | validators の knowledge-checks |
| [検査と変換のスクリプト / scripts / knowledge_markdown.py](./MOD-72-5.py.yaml) | converters の knowledge-markdown |
| [検査と変換のスクリプト / scripts](./MOD-72-1.yaml) | 検査と変換のスクリプトの構成・起動の方式・テストの配置先 |
| [slop-check / hooks](./MOD-148-1.yaml) | プラグイン slop-check のフックの構成・起動の方式・照合の共有 |

<!-- /table -->
