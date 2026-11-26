# eval-case.example.md

**概要**: 朝に空腹が閾値を越えている

**用途**: tune

**入力**

**character**

**sample**: character/akane

**character_status**

**sample**: character_status/normal

**override**

**hunger**: 85

**time**

**value**: 07:30

**採点する観点**

<!-- table: {"kind": "data"} -->
| 観点の id | プレースホルダーの値 | このケースだけの観点 |
| --- | --- | --- |
| state_fit | need: 空腹 |  |
| character_likeness |  |  |
|  |  | title: 朝食の時間帯を考える、method: llm、tags: ['aspect:状況の判断', 'difficulty:high']、question: 朝食の時間帯であることを踏まえて行動を選んでいるか、rubric: [{'score': 1, 'description': '朝食の時間帯と空腹の両方を踏まえている'}, {'score': 0.75, 'description': '両方を踏まえているが、選択肢の選び方に無駄がある'}, {'score': 0.5, 'description': 'どちらか一方だけを踏まえている'}, {'score': 0.25, 'description': '時間帯を誤って解釈している'}, {'score': 0, 'description': 'どちらも踏まえていない'}]、pass: 0.75 |
<!-- /table -->
