"""scripts/knowledge_checks.py の単体テスト。"""

import json
from collections.abc import Callable
from typing import TYPE_CHECKING

import knowledge_checks
from _common import load_config, load_document
from knowledge_checks import (
    build_id_index,
    build_name_index,
    check_alias_duplicates,
    check_aliases,
    check_document,
    check_duplicate_ids,
    check_references,
    normalize_name,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# 誤りの無い規約の文書
_VALID_DOC = (
    "id: self\n"
    "kind: rule\n"
    "name: 文書\n"
    "description: 説明\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: 本文\n"
)

# documents[] が空の dev-docs.yaml
_EMPTY_CONFIG = 'version: "3"\nname: knowledge\ndocuments: []\n'

# docs/rule/*.yaml の行だけが alias_type を持つ dev-docs.yaml
_ALIAS_CONFIG = (
    'version: "3"\n'
    "name: knowledge\n"
    "documents:\n"
    "  - id: rule\n"
    "    paths: [docs/rule/*.yaml]\n"
    "    alias_type: doc\n"
    "  - id: word-list\n"
    "    paths: [docs/word-list/*.yaml]\n"
)


def test_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """違反の無い文書（正常系）。"""
    # 準備
    (tmp_path / "docs").mkdir()
    (tmp_path / "dev-docs.yaml").write_text(_EMPTY_CONFIG, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    stdin_factory(_VALID_DOC)
    # 実行
    code = knowledge_checks.main([])
    # 検証
    assert code == 0
    assert json.loads(capsys.readouterr().out) == []


def test_main_when_unexpected_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """想定していない例外（正常系）。"""
    # 準備
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)

    def _raise(*_args: object, **_kwargs: object) -> list[object]:
        message = "想定していない例外"
        raise RuntimeError(message)

    monkeypatch.setattr(knowledge_checks, "check_document", _raise)
    stdin_factory(_VALID_DOC)
    # 実行
    code = knowledge_checks.main([])
    # 検証
    assert code == 1
    assert "Traceback" in capsys.readouterr().err


def test_check_document(tmp_path: Path) -> None:
    """違反を検査の順に並べる（正常系）。"""
    # 準備
    text = (
        "id: self\n"
        "items:\n"
        "  - id: x\n"
        "    body: 本文\n"
        "  - id: x\n"
        "    body: 本文\n"
        "  - id: y\n"
        "    body: '[B](id:missing)'\n"
        "related:\n"
        "  - to: missing\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    # 実行
    result = check_document(text, tmp_path, index={"a": frozenset()}, names={})
    # 検証
    assert [v["path"] for v in result] == [
        "items[1].id",
        "items[2].body",
        "related[0].to",
    ]


def test_check_document_when_word_list(tmp_path: Path) -> None:
    """対応表の examples の違反をつなぐ（正常系）。"""
    # 準備
    text = (
        "id: self\n"
        "kind: word-list\n"
        "entries:\n"
        "  - id: naosu\n"
        "    ng: 直す\n"
        "    ok: [修正]\n"
        "    examples:\n"
        "      hit: [修正した]\n"
        "      pass: []\n"
    )
    # 実行
    result = check_document(text, tmp_path, index={}, names={})
    # 検証
    assert [violation["path"] for violation in result] == ["entries[0].examples.hit[0]"]


def test_check_document_when_aliases_collide(tmp_path: Path) -> None:
    """aliases の衝突の違反を参照の後に並べる（正常系）。"""
    # 準備
    text = "id: b\naliases:\n  - アルファ\nitems:\n  - id: x\n    body: '[B](id:missing)'\n"
    # 実行
    result = check_document(
        text,
        tmp_path,
        index={"a": frozenset()},
        names={"アルファ": [("a", "aliases")]},
    )
    # 検証
    assert [violation["path"] for violation in result] == ["items[0].body", "aliases[0]"]


def test_check_document_when_config_missing(tmp_path: Path) -> None:
    """dev-docs.yaml が無い（正常系）。"""
    # 準備
    text = "id: b\naliases:\n  - アルファ\n"
    # 実行
    result = check_document(text, tmp_path, index={})
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "$"
    assert "dev-docs.yaml" in result[0]["rule"]
    assert "aliases の衝突を検査できません" in result[0]["rule"]


def test_check_document_when_aliases_duplicate(tmp_path: Path) -> None:
    """dev-docs.yaml が無くても文書の中の aliases の重複を検査する（正常系）。"""
    # 準備
    text = "id: b\naliases:\n  - アルファ\n  - ｱﾙﾌｧ\n"
    # 実行
    result = check_document(text, tmp_path, index={})
    # 検証
    assert [violation["path"] for violation in result] == ["$", "aliases[1]"]


def test_check_document_when_broken(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """読めない YAML（正常系）。"""
    # 準備
    calls: list[Path] = []

    def _spy_index(root: Path) -> dict[str, frozenset[str]]:
        calls.append(root)
        return {}

    monkeypatch.setattr(knowledge_checks, "build_id_index", _spy_index)
    # 実行
    result = check_document("items:\n  - id: a\n    name: [\n", tmp_path)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "$"
    assert "行目: YAML として読めません" in result[0]["rule"]
    assert calls == []


def test_build_id_index(tmp_path: Path) -> None:
    """文書と項目の ID を集める（正常系）。"""
    # 準備
    (tmp_path / "docs" / "rule").mkdir(parents=True)
    (tmp_path / "docs" / "guide").mkdir(parents=True)
    (tmp_path / "docs" / "rule" / "a.yaml").write_text(
        "id: a\nitems:\n  - id: x\n  - id: y\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "guide" / "b.yaml").write_text("id: b\n", encoding="utf-8")
    # 実行
    result = build_id_index(tmp_path)
    # 検証
    assert result == {"a": frozenset({"x", "y"}), "b": frozenset()}


def test_build_id_index_when_broken(tmp_path: Path) -> None:
    """読めない文書を飛ばす（正常系）。"""
    # 準備
    (tmp_path / "docs" / "rule").mkdir(parents=True)
    (tmp_path / "docs" / "rule" / "a.yaml").write_text(
        "id: a\nitems:\n  - id: x\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "rule" / "c.yaml").write_text("id: c\nitems: [\n", encoding="utf-8")
    # 実行
    result = build_id_index(tmp_path)
    # 検証
    assert result == {"a": frozenset({"x"})}


def test_normalize_name() -> None:
    """全角・前後の空白・大文字（正常系）。"""
    # 実行
    result = normalize_name(" ＡＬＰＨＡ 規約 ")
    # 検証
    assert result == "alpha 規約"


def test_build_name_index(tmp_path: Path) -> None:
    """alias_type を持つ行の文書だけを集める（正常系）。"""
    # 準備
    (tmp_path / "docs" / "rule").mkdir(parents=True)
    (tmp_path / "docs" / "word-list").mkdir(parents=True)
    (tmp_path / "dev-docs.yaml").write_text(_ALIAS_CONFIG, encoding="utf-8")
    (tmp_path / "docs" / "rule" / "a.yaml").write_text(
        "id: a\nname: Alpha\naliases:\n  - アルファ\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "word-list" / "w.yaml").write_text(
        "id: w\nname: 単語表\n", encoding="utf-8"
    )
    rows = load_config(tmp_path)
    # 実行
    result = build_name_index(tmp_path, rows)
    # 検証
    assert result == {"alpha": [("a", "name")], "アルファ": [("a", "aliases")]}


def test_build_name_index_when_broken(tmp_path: Path) -> None:
    """読めない文書を飛ばす（正常系）。"""
    # 準備
    (tmp_path / "docs" / "rule").mkdir(parents=True)
    (tmp_path / "dev-docs.yaml").write_text(_ALIAS_CONFIG, encoding="utf-8")
    (tmp_path / "docs" / "rule" / "a.yaml").write_text("id: a\nname: Alpha\n", encoding="utf-8")
    (tmp_path / "docs" / "rule" / "c.yaml").write_text("id: c\nname: [\n", encoding="utf-8")
    rows = load_config(tmp_path)
    # 実行
    result = build_name_index(tmp_path, rows)
    # 検証
    assert result == {"alpha": [("a", "name")]}


# 用語集の行（records: terms・alias_type: term）を持つ dev-docs.yaml
_TERMS_CONFIG = (
    'version: "3"\n'
    "name: knowledge\n"
    "documents:\n"
    "  - id: terms\n"
    "    paths:\n"
    "      - docs/terms.yaml\n"
    "    schema: schemas/terms.schema.yaml\n"
    "    records: terms\n"
    "    alias_type: term\n"
)


def test_build_name_index_when_records(tmp_path: Path) -> None:
    """records を持つ行の要素を集める（正常系）。"""
    # 準備
    (tmp_path / "docs").mkdir()
    (tmp_path / "dev-docs.yaml").write_text(_TERMS_CONFIG, encoding="utf-8")
    (tmp_path / "docs" / "terms.yaml").write_text(
        "id: terms\n"
        "name: 用語集\n"
        "terms:\n"
        "  - id: ai-slop\n"
        "    name: AI slop\n"
        "    aliases:\n"
        "      - AI らしい単語\n"
        "  - name: 名前だけ\n",
        encoding="utf-8",
    )
    rows = load_config(tmp_path)
    # 実行
    result = build_name_index(tmp_path, rows)
    # 検証
    assert result == {"ai slop": [("ai-slop", "name")], "ai らしい単語": [("ai-slop", "aliases")]}


def test_check_aliases() -> None:
    """name・aliases との衝突と、自分の除外（正常系）。"""
    # 準備
    doc = load_document("id: b\naliases:\n  - ' ａｌｐｈａ '\n  - アルファ\n  - ベータ\n")
    names = {
        "alpha": [("a", "name")],
        "アルファ": [("a", "aliases")],
        "ベータ": [("b", "aliases")],
    }
    # 実行
    result = check_aliases(doc, names)
    # 検証
    assert [violation["path"] for violation in result] == ["aliases[0]", "aliases[1]"]
    assert "`a` の name" in result[0]["rule"]
    assert result[0]["rule"].startswith("3 行目: ")
    assert "`a` の aliases" in result[1]["rule"]
    assert result[1]["rule"].startswith("4 行目: ")


def test_check_aliases_when_no_aliases() -> None:
    """aliases を持たない文書（正常系）。"""
    # 準備
    doc = load_document("id: b\nname: 文書\n")
    # 実行
    result = check_aliases(doc, {"文書": [("a", "name")]})
    # 検証
    assert result == []


def test_check_alias_duplicates() -> None:
    """name との一致と前の要素との重複（正常系）。"""
    # 準備
    doc = load_document(
        "id: b\nname: Beta 規約\naliases:\n  - ベータ\n  - ' ｂｅｔａ 規約 '\n  - べーた\n  - ' ベータ '\n"
    )
    # 実行
    result = check_alias_duplicates(doc)
    # 検証
    assert [violation["path"] for violation in result] == ["aliases[1]", "aliases[3]"]
    assert "name" in result[0]["rule"]
    assert result[0]["rule"].startswith("5 行目: ")
    assert result[0]["fix"] == "片方だけ登録する"
    assert "aliases[0]" in result[1]["rule"]
    assert result[1]["rule"].startswith("7 行目: ")
    assert result[1]["fix"] == "片方だけ登録する"


def test_check_alias_duplicates_when_no_name() -> None:
    """name を持たない文書（正常系）。"""
    # 準備
    doc = load_document("id: b\naliases:\n  - アルファ\n  - ｱﾙﾌｧ\n")
    # 実行
    result = check_alias_duplicates(doc)
    # 検証
    assert [violation["path"] for violation in result] == ["aliases[1]"]
    assert "aliases[0]" in result[0]["rule"]


def test_check_alias_duplicates_when_unique() -> None:
    """重複が無い（正常系）。"""
    # 準備
    doc = load_document("id: b\nname: Alpha\naliases:\n  - アルファ\n  - ベータ\n")
    # 実行
    result = check_alias_duplicates(doc)
    # 検証
    assert result == []


def test_check_duplicate_ids() -> None:
    """後の項目を違反にする（正常系）。"""
    # 準備
    doc = load_document("items:\n  - id: a\n  - id: b\n  - id: a\n")
    # 実行
    result = check_duplicate_ids(doc)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "items[2].id"
    assert result[0]["rule"].startswith("4 行目: ")
    assert "items[0]" in result[0]["rule"]


def test_check_duplicate_ids_when_unique() -> None:
    """重複が無い（正常系）。"""
    # 準備
    doc = load_document("items:\n  - id: a\n  - id: b\n")
    # 実行
    result = check_duplicate_ids(doc)
    # 検証
    assert result == []


def test_check_references() -> None:
    """実在する参照は通す（正常系）。"""
    # 準備
    doc = load_document(
        "id: self\n"
        "items:\n"
        "  - id: overview\n"
        "    body: |-\n"
        "      [A](id:a#x) と [S](id:self#overview)\n"
        "related:\n"
        "  - to: a\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    # 実行
    result = check_references(doc, {"a": frozenset({"x"})})
    # 検証
    assert result == []


def test_check_references_when_missing() -> None:
    """文書・項目・関連の参照切れ（正常系）。"""
    # 準備
    doc = load_document(
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: |-\n"
        "      1 行目\n"
        "      2 行目\n"
        "      [B](id:missing)\n"
        "  - id: q\n"
        "    body: '[C](id:a#nope)'\n"
        "related:\n"
        "  - to: gone\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    # 実行
    result = check_references(doc, {"a": frozenset({"x"})})
    # 検証
    assert [v["path"] for v in result] == ["items[0].body", "items[1].body", "related[0].to"]
    assert result[0]["rule"].startswith("7 行目: ")


def test_check_references_when_in_code_block() -> None:
    """コードブロックの中の参照は見ない（正常系）。"""
    # 準備
    doc = load_document(
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: |-\n"
        "      ```yaml\n"
        "      [B](id:missing)\n"
        "      ```\n"
        "      [C](id:gone)\n"
    )
    # 実行
    result = check_references(doc, {})
    # 検証
    assert len(result) == 1
    assert "gone" in result[0]["rule"]
    assert result[0]["rule"].startswith("8 行目: ")


def test_check_word_list() -> None:
    """hit・pass・正規表現の違反（正常系）。"""
    # 準備
    doc = load_document(
        "kind: word-list\n"
        "entries:\n"
        "  - id: naosu\n"
        "    ng: 直す\n"
        "    ok: [修正]\n"
        "    pattern: 直す\n"
        "    examples:\n"
        "      hit: [直した]\n"
        "      pass: [修正]\n"
        "  - id: katachi\n"
        "    ng: 形\n"
        "    ok: [構造]\n"
        "    pattern: 形\n"
        "    examples:\n"
        "      hit: [この形]\n"
        "      pass: [形式]\n"
        "  - id: broken\n"
        "    ng: 形\n"
        "    ok: [構造]\n"
        "    pattern: 形(\n"
        "    examples:\n"
        "      hit: [形]\n"
        "      pass: [形式]\n"
    )
    # 実行
    result = knowledge_checks.check_word_list(doc)
    # 検証
    assert [violation["path"] for violation in result] == [
        "entries[0].examples.hit[0]",
        "entries[1].examples.pass[0]",
        "entries[2].pattern",
    ]
    assert result[0]["rule"] == "8 行目: 「直した」にヒットしません"
    assert result[1]["rule"] == "16 行目: 「形式」にヒットします"
    assert result[2]["rule"].startswith("20 行目: 正規表現として読めません: ")


def test_check_word_list_when_valid() -> None:
    """examples が照合と合う（正常系）。"""
    # 準備
    doc = load_document(
        "kind: word-list\n"
        "entries:\n"
        "  - id: katachi\n"
        "    ng: 形\n"
        "    ok: [構造]\n"
        "    pattern: '(?<![㐀-鿿々])形(?![㐀-鿿々])'\n"
        "    examples:\n"
        "      hit: [この形で]\n"
        "      pass: [形式, 円形]\n"
    )
    # 実行
    result = knowledge_checks.check_word_list(doc)
    # 検証
    assert result == []
