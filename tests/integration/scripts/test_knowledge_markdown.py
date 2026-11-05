"""文書の Markdown への変換（scripts/knowledge_markdown.py）の結合テスト。"""

import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from _common import load_safe

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]

# スキーマを読む配信元。リポジトリの直下の schemas/ を使う
_ROOT = Path(__file__).resolve().parents[3]

# 項目の本文。元の Markdown のまま出ることを確かめる
_BODY_OVERVIEW = "エージェントが書く文章の確認と、語の選び方の決まり。"
_BODY_LABEL = "文章でない所は、IT の分野で定着した語で書く。\n\n<!-- table: data -->\n\n| 語 | 例 |\n| --- | --- |\n| 送信 | `送る` |\n\n<!-- /table -->"
_BODY_PRINCIPLE = "対応表に無い語は、[語の選び方](id:flowchart-word-choice) で判断する。"


# 埋め込みのマーカーの行と、コードブロックの中の同じマーカーを持つ本文
_BODY_EMBED = (
    "<!-- embed: word-list-ai-slop -->\n\n"
    "NG の単語と置き換え先は、対応表に従う。\n\n"
    "```markdown\n<!-- embed: word-list-ai-slop -->\n```"
)

# 埋め込む対応表
_WORD_LIST = _ROOT / "docs" / "word-list" / "word-list-ai-slop.yaml"


def _embed_rule(body: str) -> str:
    """本文 1 つの項目を持つ規約の文書の YAML を作る。"""
    return (
        "id: a\nkind: rule\nname: 規約\ndescription: 説明\n"
        "items:\n  - id: t-01\n    name: 表\n    body: |-\n"
        f"{_indent(body)}\n"
    )


def _indent(text: str) -> str:
    """YAML のブロックの本文として、各行に 6 つの空白を付ける。"""
    return "\n".join(f"      {line}" if line else "" for line in text.split("\n"))


def _split_word_list_table(stdout: str) -> tuple[list[str], str]:
    """変換の出力を、NG・OK の表の行の並びと、表の外の残りに分ける。"""
    before, after = stdout.split("| NG | OK |\n| --- | --- |\n", 1)
    table, rest = after.split("\n\n", 1)
    return table.split("\n"), before + rest


def _word_list_rows(entries: list[dict[str, Any]]) -> list[str]:
    """対応表の行の ng・ok・note から、NG・OK の表の行を作る。セルの | は \\| にする。"""
    rows: list[str] = []
    for entry in entries:
        ok = "・".join(str(word) for word in entry.get("ok", []))
        # note がある行: OK の列の末尾に括弧書きで付ける
        if entry.get("note"):
            ok += f"（{entry['note']}）"
        ng = str(entry["ng"]).replace("|", "\\|")
        ok = ok.replace("|", "\\|")
        rows.append(f"| {ng} | {ok} |")
    return rows


def _leaked_match_values(entries: list[dict[str, Any]], stdin: str, outside: str) -> list[str]:
    """照合の値（pattern・allow・examples）のうち、入力の文書に無く表の外に出た値を返却する。"""
    values: list[str] = []
    for entry in entries:
        examples = entry.get("examples", {})
        values += [str(entry["pattern"])] if "pattern" in entry else []
        values += [str(value) for value in entry.get("allow", [])]
        values += [str(value) for value in examples.get("hit", []) + examples.get("pass", [])]
    # 入力の本文に含まれる値は、変換が追加した値でなくても表の外に出るため除く
    return [value for value in values if value not in stdin and value in outside]


def test_normal(run_script: RunScript) -> None:
    """規約を、group の階層を見出しにした Markdown にする（正常系）。"""
    # 準備
    stdin = (
        "id: convention-writing-style\n"
        "kind: rule\n"
        "name: 文章の書き方\n"
        "description: 文章の確認表と語の選び方を定める。\n"
        "items:\n"
        "  - id: overview\n"
        "    name: 概要\n"
        "    body: |-\n"
        f"{_indent(_BODY_OVERVIEW)}\n"
        "  - id: word-choice-01\n"
        "    group: 語の選び方\n"
        "    name: 文章でない所の語の選び方\n"
        "    body: |-\n"
        f"{_indent(_BODY_LABEL)}\n"
        "  - id: word-choice-principle-01\n"
        "    group: 語の選び方 > 原則\n"
        "    name: 対応表に無い語の判断\n"
        "    body: |-\n"
        f"{_indent(_BODY_PRINCIPLE)}\n"
        "  - id: word-choice-principle-02\n"
        "    group: 語の選び方 > 原則\n"
        "    name: 語の選び方の原則表\n"
        "    body: 原則の表\n"
        "related:\n"
        "  - to: flowchart-word-choice\n"
        "    type: references\n"
        "    when: 迷ったとき\n"
        "  - to: convention-keep-existing-text\n"
        "    type: see_also\n"
        "    when: 既存の文書を編集するとき\n"
    )
    # 実行
    result = run_script("knowledge_markdown", _ROOT, stdin)
    # 検証
    lines = result.stdout.split("\n")
    # 「## 語の選び方」から「### 原則」までの間に、別の ## の見出しが無い
    between = result.stdout.split("\n## 語の選び方\n", 1)[1].split("\n### 原則\n", 1)[0]
    related = result.stdout.split("## 関連\n", 1)[1]
    assert result.exit_code == 0
    assert result.stdout.startswith("# 文章の書き方\n")
    assert "\n## " not in between
    assert lines.count("### 原則") == 1
    assert _BODY_OVERVIEW in result.stdout
    assert _BODY_LABEL in result.stdout
    assert _BODY_PRINCIPLE in result.stdout
    assert [line for line in related.split("\n") if line.startswith("- ")] == [
        "- [flowchart-word-choice](id:flowchart-word-choice)（references）: 迷ったとき",
        "- [convention-keep-existing-text](id:convention-keep-existing-text)（see_also）: 既存の文書を編集するとき",
    ]


def test_normal_when_kind_specific_keys(run_script: RunScript) -> None:
    """スキルの固有のキーを、スキーマの title を見出しにした節で出す（正常系）。"""
    # 準備
    stdin = (
        "id: text-review\n"
        "kind: skill\n"
        "name: 文章の点検\n"
        "description: 文章を点検する。\n"
        "arguments:\n"
        "  - name: target\n"
        "    description: 点検する範囲\n"
        "preconditions:\n"
        "  - 作業ツリーがある\n"
        "  - 規約を読める\n"
        "items:\n"
        "  - id: overview\n"
        "    name: 概要\n"
        "    body: スキルの概要\n"
    )
    # 実行
    result = run_script("knowledge_markdown", _ROOT, stdin)
    # 検証
    assert result.exit_code == 0
    assert "## 引数\n\n<!-- table: data -->\n\n" in result.stdout
    assert "| target | 点検する範囲 |" in result.stdout
    assert "## 事前条件\n\n- 作業ツリーがある\n- 規約を読める\n" in result.stdout


def test_error_when_schema_missing(run_script: RunScript) -> None:
    """kind のスキーマが無ければ変換せずに終わる（異常系）。"""
    # 準備
    stdin = "id: a\nkind: missing\nname: A\ndescription: A の文書\n"
    # 実行
    result = run_script("knowledge_markdown", _ROOT, stdin)
    # 検証
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "schemas/missing.schema.yaml" in result.stderr


def test_error_when_invalid_yaml(run_script: RunScript) -> None:
    """読めない入力は変換せずに終わる（異常系）。"""
    # 準備
    stdin = "items:\n  - id: a\n    name: [\n"
    # 実行
    result = run_script("knowledge_markdown", _ROOT, stdin)
    # 検証
    assert result.exit_code == 1
    assert " 行目: YAML として読めません" in result.stderr


def test_normal_when_embed_marker(run_script: RunScript) -> None:
    """項目の本文の埋め込みのマーカーを、ID の対応表の NG・OK の表に置き換える（正常系）。"""
    # 準備
    word_list = cast("dict[str, Any]", load_safe(_WORD_LIST.read_text(encoding="utf-8")))
    entries = cast("list[dict[str, Any]]", word_list["entries"])
    stdin = _embed_rule(_BODY_EMBED)
    # 実行
    result = run_script("knowledge_markdown", _ROOT, stdin)
    # 検証
    table, outside = _split_word_list_table(result.stdout)
    assert result.exit_code == 0
    assert table == _word_list_rows(entries)
    assert result.stdout.count("<!-- embed: word-list-ai-slop -->") == 1
    assert "```markdown\n<!-- embed: word-list-ai-slop -->\n```" in result.stdout
    assert _leaked_match_values(entries, stdin, outside) == []


def test_normal_when_embed_target_missing(run_script: RunScript) -> None:
    """ID の対応表が無いマーカーは、変換を失敗させずに展開できない理由を出す（正常系）。"""
    # 実行
    result = run_script("knowledge_markdown", _ROOT, _embed_rule("<!-- embed: missing -->"))
    # 検証
    assert result.exit_code == 0
    assert "> [!WARNING]\n> 埋め込めません: missing の対応表がありません" in result.stdout


def test_error_when_word_list_unreadable(run_script: RunScript, tmp_path: Path) -> None:
    """対応表のファイルが読めなければ変換せずに終わる（異常系）。"""
    # 準備
    shutil.copytree(_ROOT / "schemas", tmp_path / "schemas")
    shutil.copy(_ROOT / "dev-docs.yaml", tmp_path / "dev-docs.yaml")
    (tmp_path / "docs" / "word-list").mkdir(parents=True)
    (tmp_path / "docs" / "word-list" / "broken.yaml").write_text(
        "entries:\n  - ng: [\n", encoding="utf-8"
    )
    # 実行
    result = run_script("knowledge_markdown", tmp_path, _embed_rule("<!-- embed: x -->"))
    # 検証
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "docs/word-list/broken.yaml の " in result.stderr
    assert " 行目が読めません" in result.stderr
