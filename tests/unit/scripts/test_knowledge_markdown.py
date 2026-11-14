"""scripts/knowledge_markdown.py の単体テスト。"""

import re
from typing import TYPE_CHECKING

import pytest

import knowledge_markdown
from _common import ConfigError
from knowledge_markdown import (
    convert,
    expand_embeds,
    has_embed,
    load_schema,
    load_word_lists,
    render_items,
    render_value,
    render_word_list,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

# 規約の文書のスキーマ（種類に固有のキー arguments の title を持つ）
_RULE_SCHEMA = "title: 規約\nproperties:\n  arguments:\n    title: 引数\n"

# Markdown の見出しの行
_HEADING = re.compile(r"^#{1,6} .*$", re.MULTILINE)

# word-list の行だけを持つ project-index.yaml
_CONFIG = 'documents:\n  - id: word-list\n    paths: ["docs/word-list/*.yaml"]\n'

# ID が x の対応表の文書
_WORD_LIST = (
    "id: x\n"
    "kind: word-list\n"
    "name: 対応表\n"
    "entries:\n"
    "  - id: kata\n"
    "    ng: 形\n"
    "    ok: [スキーマ]\n"
    "    pattern: 'x'\n"
)

# ID が x の対応表の entries
_ENTRIES = [{"id": "kata", "ng": "形", "ok": ["スキーマ"], "pattern": "x"}]

# 埋め込みのマーカーを本文に持つ rule の文書
_EMBED_RULE = (
    "id: a\nkind: rule\nname: 規約の名前\ndescription: 説明\n"
    "items:\n  - id: t-01\n    name: 表\n    body: '<!-- embed: x -->'\n"
)


def _write_repo(root: Path, word_list: str = _WORD_LIST) -> None:
    """スキーマ・project-index.yaml・対応表を持つ配信元を作る。"""
    (root / "schemas").mkdir()
    (root / "schemas" / "rule.schema.yaml").write_text(_RULE_SCHEMA, encoding="utf-8")
    (root / "project-index.yaml").write_text(_CONFIG, encoding="utf-8")
    (root / "docs" / "word-list").mkdir(parents=True)
    (root / "docs" / "word-list" / "x.yaml").write_text(word_list, encoding="utf-8")


def test_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """変換して出す（正常系）。"""
    # 準備
    (tmp_path / "schemas").mkdir()
    (tmp_path / "schemas" / "rule.schema.yaml").write_text(_RULE_SCHEMA, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    stdin_factory("id: a\nkind: rule\nname: 規約の名前\ndescription: 説明\nitems: []\n")
    # 実行
    code = knowledge_markdown.main([])
    # 検証
    assert code == 0
    assert capsys.readouterr().out.startswith("# 規約の名前")


def test_main_when_schema_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """スキーマが無い（正常系）。"""
    # 準備
    monkeypatch.chdir(tmp_path)
    stdin_factory("id: a\nkind: missing\nname: 名前\ndescription: 説明\n")
    # 実行
    code = knowledge_markdown.main([])
    # 検証
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "schemas/missing.schema.yaml" in captured.err


def test_main_when_broken(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """読めない YAML（正常系）。"""
    # 準備
    monkeypatch.chdir(tmp_path)
    stdin_factory("items:\n  - id: a\n    name: [\n")
    # 実行
    code = knowledge_markdown.main([])
    # 検証
    assert code == 1
    assert "行目: YAML として読めません" in capsys.readouterr().err


def test_main_when_embed_marker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """マーカーを展開する（正常系）。"""
    # 準備
    _write_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    stdin_factory(_EMBED_RULE)
    # 実行
    code = knowledge_markdown.main([])
    # 検証
    out = capsys.readouterr().out
    assert code == 0
    assert "| NG | OK |" in out
    assert "| 形 | スキーマ |" in out
    assert "<!-- embed:" not in out


def test_main_when_word_list_broken(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """読めない対応表（正常系）。"""
    # 準備
    _write_repo(tmp_path, word_list="entries:\n  - ng: [\n")
    monkeypatch.chdir(tmp_path)
    stdin_factory(_EMBED_RULE)
    # 実行
    code = knowledge_markdown.main([])
    # 検証
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert "docs/word-list/x.yaml" in captured.err


def test_main_when_no_marker_without_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """マーカーの無い文書は project-index.yaml を読まない（正常系）。"""
    # 準備
    (tmp_path / "schemas").mkdir()
    (tmp_path / "schemas" / "rule.schema.yaml").write_text(_RULE_SCHEMA, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    stdin_factory("id: a\nkind: rule\nname: 規約の名前\ndescription: 説明\nitems: []\n")
    # 実行
    code = knowledge_markdown.main([])
    # 検証
    assert code == 0
    assert capsys.readouterr().out.startswith("# 規約の名前")


def test_load_schema(tmp_path: Path) -> None:
    """スキーマを読む（正常系）。"""
    # 準備
    (tmp_path / "schemas").mkdir()
    (tmp_path / "schemas" / "rule.schema.yaml").write_text(_RULE_SCHEMA, encoding="utf-8")
    # 実行
    result = load_schema(tmp_path, "rule")
    # 検証
    assert result["title"] == "規約"


def test_load_schema_when_missing(tmp_path: Path) -> None:
    """スキーマが無い（異常系）。"""
    # 実行・検証
    with pytest.raises(FileNotFoundError, match=r"schemas/missing\.schema\.yaml"):
        load_schema(tmp_path, "missing")


def test_load_schema_when_no_kind(tmp_path: Path) -> None:
    """kind が無い（異常系）。"""
    # 実行・検証
    with pytest.raises(FileNotFoundError, match="文書に kind がありません"):
        load_schema(tmp_path, None)


def test_convert() -> None:
    """規約を決まった並びにする（正常系）。"""
    # 準備
    doc = {
        "id": "a",
        "kind": "rule",
        "name": "文章の書き方",
        "description": "文章の書き方を定める。",
        "tags": [{"name": "topic:文章"}],
        "rev": 3,
        "items": [
            {"id": "overview", "name": "概要", "body": "概要の本文"},
            {
                "id": "w-01",
                "group": "語の選び方",
                "name": "語の選び方の決まり",
                "body": "決まりの本文",
            },
            {"id": "w-02", "group": "語の選び方 > 原則", "name": "原則の表", "body": "原則の本文"},
        ],
        "related": [{"to": "b", "type": "references", "when": "語に迷ったとき"}],
        "sources": [
            {
                "id": "GT",
                "title": "Google Technical Writing One",
                "url": "https://developers.google.com/tech-writing/one",
            }
        ],
    }
    # 実行
    result = convert(doc, {"title": "規約"}, {})
    # 検証
    assert result.endswith("\n")
    assert _HEADING.findall(result) == [
        "# 文章の書き方",
        "## 語の選び方",
        "### 語の選び方の決まり",
        "### 原則",
        "#### 原則の表",
        "## 関連",
        "## 出典",
    ]
    assert (
        result.index("文章の書き方を定める。")
        < result.index("概要の本文")
        < result.index("## 語の選び方")
    )
    assert "- [b](id:b)（references）: 語に迷ったとき" in result
    assert (
        "- GT: [Google Technical Writing One](https://developers.google.com/tech-writing/one)"
        in result
    )
    assert "topic:文章" not in result
    assert "rev" not in result


def test_convert_when_body_has_markers() -> None:
    """本文を書き換えない（正常系）。"""
    # 準備
    body = "<!-- table: data -->\n\n| 列 | 値 |\n| --- | --- |\n| [A](id:a#x) | `x` |\n\n<!-- /table -->"
    doc = {
        "id": "a",
        "kind": "rule",
        "name": "名前",
        "description": "説明",
        "items": [{"id": "t-01", "name": "表", "body": body}],
    }
    # 実行
    result = convert(doc, {"title": "規約"}, {})
    # 検証
    assert body in result


def test_convert_when_hidden_metadata() -> None:
    """本文に出さないキー（正常系）。"""
    # 準備
    doc = {
        "id": "a",
        "kind": "rule",
        "name": "名前",
        "description": "説明",
        "aliases": ["別名の値"],
        "inject_when": {
            "or": [
                {"field": "text", "op": "contains", "values": ["照合の値"]},
            ]
        },
        "items": [],
    }
    # 実行
    result = convert(doc, {"title": "規約", "properties": {}}, {})
    # 検証
    assert _HEADING.findall(result) == ["# 名前"]
    assert "別名の値" not in result
    assert "照合の値" not in result


def test_convert_when_extra_keys() -> None:
    """種類に固有のキーを節にする（正常系）。"""
    # 準備
    doc = {
        "id": "a",
        "kind": "rule",
        "name": "名前",
        "description": "説明",
        "items": [],
        "arguments": [{"name": "x", "type": "str"}],
    }
    # 実行
    result = convert(doc, {"title": "規約", "properties": {"arguments": {"title": "引数"}}}, {})
    # 検証
    assert "## 引数\n\n<!-- table: data -->" in result


def test_convert_when_no_title_in_schema() -> None:
    """title の無いキー（正常系）。"""
    # 準備
    doc = {
        "id": "a",
        "kind": "rule",
        "name": "名前",
        "description": "説明",
        "items": [],
        "extra": "追加の値",
    }
    # 実行
    result = convert(doc, {"title": "規約", "properties": {}}, {})
    # 検証
    assert "## extra\n\n追加の値" in result


def test_convert_when_word_list() -> None:
    """対応表の entries（正常系）。"""
    # 準備
    doc = {
        "id": "a",
        "kind": "word-list",
        "name": "名前",
        "description": "説明",
        "items": [],
        "entries": [
            {
                "id": "kata",
                "ng": "形",
                "ok": ["スキーマ"],
                "pattern": "(?<![㐀-鿿々])形",
                "allow": ["形容詞"],
                "examples": {"hit": ["形を決める"], "pass": ["円形"]},
            }
        ],
    }
    # 実行
    result = convert(
        doc, {"title": "単語の対応表", "properties": {"entries": {"title": "対応表の行"}}}, {}
    )
    # 検証
    assert "## 対応表の行\n\n<!-- table: data -->\n\n| NG | OK |" in result
    assert "| 形 | スキーマ |" in result
    assert "(?<!" not in result
    assert "形を決める" not in result


def test_convert_when_overview_has_embed() -> None:
    """overview の本文のマーカー（正常系）。"""
    # 準備
    doc = {
        "id": "a",
        "kind": "rule",
        "name": "名前",
        "description": "説明",
        "items": [{"id": "overview", "name": "概要", "body": "<!-- embed: x -->"}],
    }
    # 実行
    result = convert(doc, {"title": "規約"}, {"x": _ENTRIES})
    # 検証
    assert result.startswith("# 名前\n\n説明\n\n<!-- table: data -->\n\n| NG | OK |")
    assert "<!-- embed:" not in result


def test_render_items() -> None:
    """同じ段を繰り返さない（正常系）。"""
    # 準備
    items = [
        {"id": "i1", "group": "A", "name": "一つ目", "body": "本文1"},
        {"id": "i2", "group": "A > B", "name": "二つ目", "body": "本文2"},
        {"id": "i3", "group": "A > B", "name": "三つ目", "body": "本文3"},
        {"id": "i4", "group": "C", "name": "四つ目", "body": "本文4"},
    ]
    # 実行
    result = render_items(items, {})
    # 検証
    assert _HEADING.findall("\n\n".join(result)) == [
        "## A",
        "### 一つ目",
        "### B",
        "#### 二つ目",
        "#### 三つ目",
        "## C",
        "### 四つ目",
    ]


def test_render_items_when_no_group() -> None:
    """group が無い項目（正常系）。"""
    # 準備
    items = [{"id": "i1", "name": "名前", "body": "本文"}]
    # 実行
    result = render_items(items, {})
    # 検証
    assert "\n\n".join(result) == "## 名前\n\n本文"


def test_render_items_when_too_deep() -> None:
    """深すぎる階層（正常系）。"""
    # 準備
    items = [{"id": "i1", "group": "A > B > C > D > E", "name": "名前", "body": "本文"}]
    # 実行
    result = render_items(items, {})
    # 検証
    assert _HEADING.findall("\n\n".join(result))[-1] == "###### 名前"


def test_render_items_when_embed() -> None:
    """項目の本文のマーカー（正常系）。"""
    # 準備
    items = [{"id": "i1", "name": "名前", "body": "<!-- embed: x -->\n\n文の本文。"}]
    # 実行
    result = "\n\n".join(render_items(items, {"x": _ENTRIES}))
    # 検証
    assert "| 形 | スキーマ |" in result
    assert result.endswith("\n\n文の本文。")
    assert "<!-- embed:" not in result


def test_render_value_when_string() -> None:
    """文字列（正常系）。"""
    # 実行
    result = render_value("段落")
    # 検証
    assert result == "段落"


def test_render_value_when_string_list() -> None:
    """文字列の配列（正常系）。"""
    # 実行
    result = render_value(["a", "b"])
    # 検証
    assert result == "- a\n- b"


def test_render_value_when_object_list() -> None:
    """オブジェクトの配列（正常系）。"""
    # 実行
    result = render_value([{"name": "x", "note": "a|b"}, {"name": "y"}])
    # 検証
    assert result.startswith("<!-- table: data -->")
    assert result.endswith("<!-- /table -->")
    assert "| name | note |" in result
    assert "| x | a\\|b |" in result
    assert "| y | - |" in result


def test_render_value_when_object() -> None:
    """オブジェクト（正常系）。"""
    # 実行
    result = render_value({"a": 1})
    # 検証
    assert result == "- a: 1"


def test_render_word_list() -> None:
    """NG・OK の表にする（正常系）。"""
    # 準備
    entries = [
        {
            "ng": "形",
            "ok": ["スキーマ", "構造"],
            "note": "図形は除く",
            "pattern": "(?<![㐀-鿿々])形",
            "examples": {"hit": ["形を決める"], "pass": ["円形"]},
        },
        {"ng": "節", "ok": ["セクション"]},
    ]
    # 実行
    result = render_word_list(entries)
    # 検証
    assert result.startswith("<!-- table: data -->")
    assert result.endswith("<!-- /table -->")
    assert "| NG | OK |" in result
    assert "| 形 | スキーマ・構造（図形は除く） |" in result
    assert "| 節 | セクション |" in result
    assert "(?<!" not in result


def test_has_embed() -> None:
    """マーカーがある（正常系）。"""
    # 準備
    doc = {"items": [{"id": "a", "body": "文。\n  <!-- embed: x -->  \n"}]}
    # 実行
    result = has_embed(doc)
    # 検証
    assert result is True


def test_has_embed_when_in_code_block() -> None:
    """コードブロックの中だけ（正常系）。"""
    # 準備
    doc = {
        "items": [
            {"id": "a", "body": "```\n<!-- embed: x -->\n```"},
            {"id": "b", "body": "<!-- embed: docs/a.yaml#entries -->"},
        ]
    }
    # 実行
    result = has_embed(doc)
    # 検証
    assert result is False


def test_load_word_lists(tmp_path: Path) -> None:
    """対応表を読む（正常系）。"""
    # 準備
    _write_repo(tmp_path)
    (tmp_path / "docs" / "word-list" / "r.yaml").write_text(
        "id: r\nkind: rule\nname: 規約\n", encoding="utf-8"
    )
    # 実行
    result = load_word_lists(tmp_path)
    # 検証
    assert list(result) == ["x"]
    assert result["x"][0]["ng"] == "形"


def test_load_word_lists_when_no_row(tmp_path: Path) -> None:
    """word-list の行が無い（正常系）。"""
    # 準備
    (tmp_path / "project-index.yaml").write_text(
        'documents:\n  - id: rule\n    paths: ["docs/rule/*.yaml"]\n', encoding="utf-8"
    )
    # 実行
    result = load_word_lists(tmp_path)
    # 検証
    assert result == {}


def test_load_word_lists_when_broken(tmp_path: Path) -> None:
    """読めない対応表（異常系）。"""
    # 準備
    _write_repo(tmp_path, word_list="entries:\n  - ng: [\n")
    # 実行・検証
    with pytest.raises(ConfigError, match=r"docs/word-list/x\.yaml の \d+ 行目が読めません"):
        load_word_lists(tmp_path)


def test_expand_embeds() -> None:
    """マーカーを表にする（正常系）。"""
    # 準備
    body = "<!-- embed: x -->\n\n文の本文。"
    # 実行
    result = expand_embeds(body, {"x": _ENTRIES})
    # 検証
    assert result == render_word_list(_ENTRIES) + "\n\n文の本文。"


def test_expand_embeds_when_in_code_block() -> None:
    """コードブロックの中は残す（正常系）。"""
    # 準備
    body = "```\n<!-- embed: x -->\n```\n\n~~~~\n<!-- embed: x -->\n~~~\n~~~~"
    # 実行
    result = expand_embeds(body, {"x": _ENTRIES})
    # 検証
    assert result == body


def test_expand_embeds_when_path_marker() -> None:
    """dev-docs のパスの書き方は残す（正常系）。"""
    # 準備
    body = "<!-- embed: docs/a.yaml#entries -->"
    # 実行
    result = expand_embeds(body, {"x": _ENTRIES})
    # 検証
    assert result == body


def test_expand_embeds_when_missing() -> None:
    """対応表が無い ID（正常系）。"""
    # 実行
    result = expand_embeds("<!-- embed: missing -->", {})
    # 検証
    assert result == "> [!WARNING]\n> 埋め込めません: missing の対応表がありません"
