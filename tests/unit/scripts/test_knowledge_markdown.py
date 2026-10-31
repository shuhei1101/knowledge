"""scripts/knowledge_markdown.py の単体テスト。"""

import re
from typing import TYPE_CHECKING

import pytest

import knowledge_markdown
from knowledge_markdown import convert, load_schema, render_items, render_value

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

# 規約の文書のスキーマ（種類に固有のキー arguments の title を持つ）
_RULE_SCHEMA = "title: 規約\nproperties:\n  arguments:\n    title: 引数\n"

# Markdown の見出しの行
_HEADING = re.compile(r"^#{1,6} .*$", re.MULTILINE)


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
    result = convert(doc, {"title": "規約"})
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
    result = convert(doc, {"title": "規約"})
    # 検証
    assert body in result


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
    result = convert(doc, {"title": "規約", "properties": {"arguments": {"title": "引数"}}})
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
    result = convert(doc, {"title": "規約", "properties": {}})
    # 検証
    assert "## extra\n\n追加の値" in result


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
    result = render_items(items)
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
    result = render_items(items)
    # 検証
    assert "\n\n".join(result) == "## 名前\n\n本文"


def test_render_items_when_too_deep() -> None:
    """深すぎる階層（正常系）。"""
    # 準備
    items = [{"id": "i1", "group": "A > B > C > D > E", "name": "名前", "body": "本文"}]
    # 実行
    result = render_items(items)
    # 検証
    assert _HEADING.findall("\n\n".join(result))[-1] == "###### 名前"


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
