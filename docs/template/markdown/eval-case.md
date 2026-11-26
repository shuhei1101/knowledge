# eval-case.md

**公開範囲**: public / internal

**タグ**

<!-- table: {"kind": "data"} -->
| タグの名前 | 主題 |
| --- | --- |
| {タグの名前} | true / false |
<!-- /table -->

**別名**

- {別名}

**概要**: {概要}

**用途**: tune / holdout

**採点する観点**

<!-- table: {"kind": "data"} -->
| 観点の id | 採点の基準の上書き | このケースだけの観点 |
| --- | --- | --- |
| {観点の id} | score: 0 / 0.25 / 0.5 / 0.75 / 1、description: {様子} | visibility: public / internal、aliases: ['{別名}']、title: {表示名}、method: rule / llm / human、tags: ['{タグ}']、question: {質問}、rubric: [{'score': '0 / 0.25 / 0.5 / 0.75 / 1', 'description': '{様子}'}]、pass: 0 / 0.25 / 0.5 / 0.75 / 1、check: {'function': '{関数}', 'args': {}, 'gate': 'true / false'} |
<!-- /table -->
