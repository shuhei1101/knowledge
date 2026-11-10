# post-tool-use

post-tool-use の設計書

## 目次

| ページ | 概要 |
| --- | --- |
| [slop_check.py](./slop_check.py.yaml) | プラグイン slop-check の PostToolUse のフック。書き込んだ中身を対応表のコピーで照合し、ヒットした行の通知の文を `additionalContext` で返す（IF-148-1）。 |
