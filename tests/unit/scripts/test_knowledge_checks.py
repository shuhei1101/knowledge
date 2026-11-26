"""scripts/knowledge_checks.py の単体テスト。"""

import json
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import knowledge_checks
from _common import load_config, load_document
from _lint import DEFAULT_LINT_DIR, LintFinding, LintOutputError, MdmarkCheckError
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
    from collections.abc import Callable, Sequence

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

# documents[] が空の project-index.yaml
_EMPTY_CONFIG = 'version: "3"\nname: knowledge\ndocuments: []\n'

# docs/rule/*.yaml の行だけが alias_type を持つ project-index.yaml
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
    (tmp_path / "project-index.yaml").write_text(_EMPTY_CONFIG, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    def _no_lint(*_args: object) -> list[dict[str, str]]:
        return []

    monkeypatch.setattr(knowledge_checks, "check_markdown_lints", _no_lint)
    monkeypatch.setattr(knowledge_checks, "check_yamllint", _no_lint)
    monkeypatch.setattr(knowledge_checks, "check_map", _no_lint)
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


def test_main_when_lint_violations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """lint の違反をつなぐ（正常系）。"""
    # 準備
    (tmp_path / "docs").mkdir()
    (tmp_path / "project-index.yaml").write_text(_EMPTY_CONFIG, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    lint_dir = tmp_path / "lint"
    received: list[Path] = []
    markdown = {"path": "items[0].body", "rule": "8 行目: textlint/r: m", "fix": "f"}
    yaml = {"path": "-", "rule": "1 行目: yamllint/comments: m", "fix": "f"}
    map_ = {"path": "items[0].body", "rule": "4 行目: mdmark/map_invalid: m", "fix": "f"}

    def _markdown(_text: str, lint: Path) -> list[dict[str, str]]:
        received.append(lint)
        return [markdown]

    def _yaml(_text: str, lint: Path) -> list[dict[str, str]]:
        received.append(lint)
        return [yaml]

    def _map(_text: str) -> list[dict[str, str]]:
        return [map_]

    monkeypatch.setattr(knowledge_checks, "check_markdown_lints", _markdown)
    monkeypatch.setattr(knowledge_checks, "check_yamllint", _yaml)
    monkeypatch.setattr(knowledge_checks, "check_map", _map)
    stdin_factory(_VALID_DOC)
    # 実行
    code = knowledge_checks.main(["--lint-dir", str(lint_dir)])
    # 検証
    assert code == 0
    assert json.loads(capsys.readouterr().out) == [markdown, yaml, map_]
    assert received == [lint_dir, lint_dir]


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
    """project-index.yaml が無い（正常系）。"""
    # 準備
    text = "id: b\naliases:\n  - アルファ\n"
    # 実行
    result = check_document(text, tmp_path, index={})
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "$"
    assert "project-index.yaml" in result[0]["rule"]
    assert "aliases の衝突を検査できません" in result[0]["rule"]


def test_check_document_when_aliases_duplicate(tmp_path: Path) -> None:
    """project-index.yaml が無くても文書の中の aliases の重複を検査する（正常系）。"""
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
    (tmp_path / "project-index.yaml").write_text(_ALIAS_CONFIG, encoding="utf-8")
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
    (tmp_path / "project-index.yaml").write_text(_ALIAS_CONFIG, encoding="utf-8")
    (tmp_path / "docs" / "rule" / "a.yaml").write_text("id: a\nname: Alpha\n", encoding="utf-8")
    (tmp_path / "docs" / "rule" / "c.yaml").write_text("id: c\nname: [\n", encoding="utf-8")
    rows = load_config(tmp_path)
    # 実行
    result = build_name_index(tmp_path, rows)
    # 検証
    assert result == {"alpha": [("a", "name")]}


# 用語集の行（records: terms・alias_type: term）を持つ project-index.yaml
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
    (tmp_path / "project-index.yaml").write_text(_TERMS_CONFIG, encoding="utf-8")
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


def test_check_duplicate_ids_when_aspects_duplicate() -> None:
    """観点の ID の重複を違反にし、項目とは比べない（正常系）。"""
    # 準備
    doc = load_document(
        "items:\n"
        "  - id: a\n"
        "aspects:\n"
        "  - id: a\n"
        "  - id: aspect-review-common-01\n"
        "  - id: aspect-review-common-01\n"
    )
    # 実行
    result = check_duplicate_ids(doc)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "aspects[2].id"
    assert result[0]["rule"].startswith("6 行目: ")
    assert "観点の ID" in result[0]["rule"]
    assert "aspects[1]" in result[0]["rule"]


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


def _create_lint_clis(lint_dir: Path, names: Sequence[str]) -> None:
    """lint のフォルダの node_modules/.bin/ に、実行権限のある CLI を置く。"""
    folder = lint_dir / "node_modules" / ".bin"
    folder.mkdir(parents=True)
    for name in names:
        path = folder / name
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        path.chmod(0o755)


def _fail(*_args: object) -> list[LintFinding]:
    message = "呼ばれない"
    raise AssertionError(message)


# map の範囲を items[0].body に持つ文書
_MAP_DOC = (
    "id: self\n"
    "kind: rule\n"
    "name: 文書\n"
    "description: 説明\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: |-\n"
    "      <!-- map -->\n"
    "\n"
    "      ```mermaid\n"
    "      flowchart LR\n"
    "        a --> b\n"
    "      ```\n"
    "\n"
    "      <!-- /map -->\n"
)


def test_check_markdown_lints(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """error の違反を元の文書の行で返す（正常系）。"""
    # 準備
    _create_lint_clis(tmp_path / "lint", ["markdownlint-cli2", "textlint"])
    source = PurePosixPath("-.yaml")

    def _fake(*_args: object) -> list[LintFinding]:
        return [
            LintFinding(source, 3, "items[0].body", "markdownlint", "MD019", "空白が多い", False),
            LintFinding(
                source,
                5,
                "items[0].body",
                "textlint",
                "ja-technical-writing/no-doubled-joshi",
                "助詞が重なっています",
                False,
            ),
            LintFinding(
                source,
                6,
                "items[0].body",
                "textlint",
                "one-sentence-per-line",
                "1 行に 2 文があります",
                True,
            ),
        ]

    monkeypatch.setattr(knowledge_checks, "run_markdown_lints", _fake)
    # 実行
    result = knowledge_checks.check_markdown_lints(_VALID_DOC, tmp_path / "lint")
    # 検証
    assert len(result) == 2
    assert result[0]["rule"].startswith("3 行目: markdownlint/MD019: ")
    assert result[1]["rule"].startswith("5 行目: textlint/ja-technical-writing/no-doubled-joshi: ")
    assert [violation["path"] for violation in result] == ["items[0].body", "items[0].body"]


def test_check_markdown_lints_when_no_markdown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Markdown の項目が無い（正常系）。"""
    # 準備
    text = "id: self\nkind: rule\nname: 文書\ndescription: 説明\n"
    monkeypatch.setattr(knowledge_checks, "run_markdown_lints", _fail)
    # 実行
    result = knowledge_checks.check_markdown_lints(text, tmp_path / "missing")
    # 検証
    assert result == []


def test_check_markdown_lints_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """markdownlint-cli2 が無い（正常系）。"""
    # 準備
    lint_dir = tmp_path / "lint"
    _create_lint_clis(lint_dir, ["textlint"])
    monkeypatch.setattr(knowledge_checks, "run_markdown_lints", _fail)
    # 実行
    result = knowledge_checks.check_markdown_lints(_VALID_DOC, lint_dir)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "$"
    assert "markdownlint-cli2" in result[0]["rule"]
    assert str(lint_dir) in result[0]["rule"]
    assert "textlint が" not in result[0]["rule"]
    assert "npm ci --prefix scripts/lint" in result[0]["fix"]


def test_check_markdown_lints_when_failed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI が失敗した（正常系）。"""
    # 準備
    _create_lint_clis(tmp_path / "lint", ["markdownlint-cli2", "textlint"])

    def _raise(*_args: object) -> Sequence[LintFinding]:
        message = "markdownlint-cli2 が終了コード 2 で終わりました: boom"
        raise LintOutputError(message)

    monkeypatch.setattr(knowledge_checks, "run_markdown_lints", _raise)
    # 実行
    result = knowledge_checks.check_markdown_lints(_VALID_DOC, tmp_path / "lint")
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "$"
    assert "終了コード 2" in result[0]["rule"]
    assert "boom" in result[0]["rule"]


def test_check_yamllint() -> None:
    """error の違反をファイル全体の違反で返す（正常系）。"""
    # 準備
    text = "#コメント\n" + _VALID_DOC
    # 実行
    result = knowledge_checks.check_yamllint(text, DEFAULT_LINT_DIR)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "-"
    assert result[0]["rule"].startswith("1 行目: yamllint/comments: ")


def test_check_yamllint_when_warning(tmp_path: Path) -> None:
    """warning の違反を返さない（正常系）。"""
    # 準備
    (tmp_path / ".yamllint.yaml").write_text(
        "extends: default\nrules:\n  comments:\n    level: warning\n"
        "  document-start: disable\n  line-length: disable\n",
        encoding="utf-8",
    )
    text = "#コメント\n" + _VALID_DOC
    # 実行
    result = knowledge_checks.check_yamllint(text, tmp_path)
    # 検証
    assert result == []


def test_check_yamllint_when_broken(monkeypatch: pytest.MonkeyPatch) -> None:
    """読み込めない YAML（正常系）。"""
    # 準備
    monkeypatch.setattr(knowledge_checks, "run_yamllint", _fail)
    # 実行
    result = knowledge_checks.check_yamllint("items:\n  - id: a\n    name: [", DEFAULT_LINT_DIR)
    # 検証
    assert result == []


def test_check_map(monkeypatch: pytest.MonkeyPatch) -> None:
    """map のずれを元の文書の行で返す（正常系）。"""
    # 準備
    source = PurePosixPath("-.yaml")

    def _fake(*_args: object) -> list[LintFinding]:
        return [LintFinding(source, 4, "items[0].body", "mdmark", "map_invalid", "描けない", False)]

    monkeypatch.setattr(knowledge_checks.shutil, "which", lambda _name: "/usr/bin/npx")
    monkeypatch.setattr(knowledge_checks, "run_map_check", _fake)
    # 実行
    result = knowledge_checks.check_map(_MAP_DOC)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "items[0].body"
    assert result[0]["rule"].startswith("4 行目: mdmark/map_invalid: ")


def test_check_map_when_no_map(monkeypatch: pytest.MonkeyPatch) -> None:
    """map を含む項目が無い（正常系）。"""
    # 準備
    monkeypatch.setattr(knowledge_checks.shutil, "which", _fail)
    monkeypatch.setattr(knowledge_checks, "run_map_check", _fail)
    # 実行
    result = knowledge_checks.check_map(_VALID_DOC)
    # 検証
    assert result == []


def test_check_map_when_npx_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """npx が無い（正常系）。"""
    # 準備
    monkeypatch.setattr(knowledge_checks.shutil, "which", lambda _name: None)
    monkeypatch.setattr(knowledge_checks, "run_map_check", _fail)
    # 実行
    result = knowledge_checks.check_map(_MAP_DOC)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "$"
    assert "npx" in result[0]["rule"]
    assert "Node 24" in result[0]["fix"]


def test_check_map_when_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """mdmark の点検が失敗した（正常系）。"""
    # 準備

    def _raise(*_args: object) -> Sequence[LintFinding]:
        message = "mdmark が終了コード 2 で終わりました: boom"
        raise MdmarkCheckError(message)

    monkeypatch.setattr(knowledge_checks.shutil, "which", lambda _name: "/usr/bin/npx")
    monkeypatch.setattr(knowledge_checks, "run_map_check", _raise)
    # 実行
    result = knowledge_checks.check_map(_MAP_DOC)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "$"
    assert "終了コード 2" in result[0]["rule"]
    assert "boom" in result[0]["rule"]
