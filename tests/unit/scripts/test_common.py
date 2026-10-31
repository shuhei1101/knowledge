"""scripts/_common.py の単体テスト。"""

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

import pytest
from ruamel.yaml.comments import CommentedMap

from _common import (
    ConfigError,
    DocumentError,
    format_path,
    iter_strings,
    line_of,
    list_row_files,
    load_config,
    load_document,
    read_texts,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_load_document() -> None:
    """マッピングの文書を読む（正常系）。"""
    # 準備
    text = "id: a\nitems:\n  - id: x\n"
    # 実行
    doc = load_document(text)
    # 検証
    assert isinstance(doc, CommentedMap)
    assert doc.lc.key("items") == (1, 0)


def test_load_document_when_broken() -> None:
    """読めない YAML（異常系）。"""
    # 準備
    text = "items:\n  - id: a\n    name: [\n"
    # 実行・検証
    with pytest.raises(DocumentError) as raised:
        load_document(text)
    assert raised.value.line >= 3


def test_load_document_when_not_mapping() -> None:
    """最上位が配列（異常系）。"""
    # 準備
    text = "- a\n"
    # 実行・検証
    with pytest.raises(DocumentError, match="最上位がマッピングではありません") as raised:
        load_document(text)
    assert raised.value.line == 1


def test_format_path() -> None:
    """キーと添字をつなぐ（正常系）。"""
    # 実行
    result = format_path(["items", 3, "body"])
    # 検証
    assert result == "items[3].body"


def test_format_path_when_empty() -> None:
    """文書全体（正常系）。"""
    # 実行
    result = format_path([])
    # 検証
    assert result == "$"


def test_iter_strings() -> None:
    """入れ子の文字列をパスと行で返す（正常系）。"""
    # 準備
    doc = load_document(
        "id: a\nrev: 1\nitems:\n  - id: x\n    body: |-\n      本文の 1 行目\n      本文の 2 行目\n"
    )
    # 実行
    result = list(iter_strings(doc))
    # 検証
    assert result == [
        (("id",), 1, "a"),
        (("items", 0, "id"), 4, "x"),
        (("items", 0, "body"), 6, "本文の 1 行目\n本文の 2 行目"),
    ]


def test_iter_strings_when_flow_scalar() -> None:
    """1 行の文字列は同じ行（正常系）。"""
    # 準備
    doc = load_document("id: a\ndescription: 説明\n")
    # 実行
    result = list(iter_strings(doc))
    # 検証
    assert result[1] == (("description",), 2, "説明")


def test_read_texts(tmp_path: Path) -> None:
    """全てのファイルを読む（正常系）。"""
    # 準備
    first = tmp_path / "c.yaml"
    second = tmp_path / "a.yaml"
    third = tmp_path / "b.yaml"
    first.write_text("シー", encoding="utf-8")
    second.write_text("エー", encoding="utf-8")
    third.write_text("ビー", encoding="utf-8")
    # 実行
    result = read_texts([first, second, third])
    # 検証
    assert list(result.items()) == [(first, "シー"), (second, "エー"), (third, "ビー")]


def test_read_texts_when_unreadable(tmp_path: Path) -> None:
    """読めないファイルは None（正常系）。"""
    # 準備
    missing = tmp_path / "missing.yaml"
    sjis = tmp_path / "sjis.yaml"
    sjis.write_bytes("規約".encode("shift_jis"))
    # 実行
    result = read_texts([missing, sjis])
    # 検証
    assert result == {missing: None, sjis: None}


def test_line_of() -> None:
    """入れ子のキーの行（正常系）。"""
    # 準備
    doc = load_document(
        "id: a\nname: 文書\nitems:\n  - id: x\n    name: 一つ目\n  - id: y\n    name: 二つ目\n"
    )
    # 実行
    result = line_of(doc, ["items", 1, "name"])
    # 検証
    assert result == 7


def test_line_of_when_missing() -> None:
    """無いキーは親の行（正常系）。"""
    # 準備
    doc = load_document(
        "id: a\nname: 文書\nitems:\n  - id: x\n    name: 一つ目\n  - id: y\n    name: 二つ目\n"
    )
    # 実行
    result = line_of(doc, ["items", 1, "nope"])
    # 検証
    assert result == 6


def test_line_of_when_empty() -> None:
    """文書全体（正常系）。"""
    # 準備
    doc = load_document("id: a\nname: 文書\n")
    # 実行
    result = line_of(doc, [])
    # 検証
    assert result == 1


def test_load_config(tmp_path: Path) -> None:
    """行を読む（正常系）。"""
    # 準備
    (tmp_path / "dev-docs.yaml").write_text(
        "name: knowledge\n"
        "documents:\n"
        "  - id: rule\n"
        "    paths:\n"
        "      - docs/rule/*.yaml\n"
        "    schema: schemas/rule.schema.yaml\n"
        "  - id: guide\n"
        "    paths:\n"
        "      - docs/guide/*.yaml\n"
        "    schema: schemas/guide.schema.yaml\n",
        encoding="utf-8",
    )
    # 実行
    result = load_config(tmp_path)
    # 検証
    assert len(result) == 2


def test_load_config_when_missing(tmp_path: Path) -> None:
    """ファイルが無い（異常系）。"""
    # 実行・検証
    with pytest.raises(ConfigError, match=r"dev-docs\.yaml がありません"):
        load_config(tmp_path)


def test_load_config_when_broken(tmp_path: Path) -> None:
    """YAML として読めない（異常系）。"""
    # 準備
    (tmp_path / "dev-docs.yaml").write_text("name: knowledge\ndocuments: [\n", encoding="utf-8")
    # 実行・検証
    with pytest.raises(ConfigError, match=r"dev-docs\.yaml の \d+ 行目が読めません"):
        load_config(tmp_path)


def test_load_config_when_no_documents(tmp_path: Path) -> None:
    """documents が無い（異常系）。"""
    # 準備
    (tmp_path / "dev-docs.yaml").write_text("name: knowledge\n", encoding="utf-8")
    # 実行・検証
    with pytest.raises(ConfigError, match=r"dev-docs\.yaml に documents の配列がありません"):
        load_config(tmp_path)


def test_list_row_files(tmp_path: Path) -> None:
    """行のパターンで引く（正常系）。"""
    # 準備
    (tmp_path / "docs" / "rule").mkdir(parents=True)
    (tmp_path / "docs" / "rule" / "b.yaml").write_text("id: b\n", encoding="utf-8")
    (tmp_path / "docs" / "rule" / "a.yaml").write_text("id: a\n", encoding="utf-8")
    (tmp_path / "docs" / "rule" / "index.yaml").write_text("items: []\n", encoding="utf-8")
    row = {"id": "rule", "paths": ["docs/rule/*.yaml"], "exclude": ["index.yaml"]}
    # 実行
    result = list_row_files(tmp_path, row)
    # 検証
    assert result == [PurePosixPath("docs/rule/a.yaml"), PurePosixPath("docs/rule/b.yaml")]


def test_list_row_files_when_disabled(tmp_path: Path) -> None:
    """無効な行（正常系）。"""
    # 準備
    (tmp_path / "docs" / "guide").mkdir(parents=True)
    (tmp_path / "docs" / "guide" / "g.yaml").write_text("id: g\n", encoding="utf-8")
    row = {"id": "guide", "paths": ["docs/guide/*.yaml"], "enabled": False}
    # 実行
    result = list_row_files(tmp_path, row)
    # 検証
    assert result == []
