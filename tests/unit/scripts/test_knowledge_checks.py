"""scripts/knowledge_checks.py の単体テスト。"""

import json
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

import knowledge_checks
from _common import load_document
from knowledge_checks import (
    build_id_index,
    check_document,
    check_duplicate_ids,
    check_mermaid,
    check_references,
    mermaid_blocks,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

type FakeMaidFactory = Callable[..., str]

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

# items[3].body の mermaid のブロックの中身が 40 行目から始まる文書（本文の 1 行目が 11 行目、囲みが 39 行目）
_MERMAID_AT_40 = (
    "id: self\n"
    "items:\n"
    "  - id: a\n"
    "    body: x\n"
    "  - id: b\n"
    "    body: x\n"
    "  - id: c\n"
    "    body: x\n"
    "  - id: d\n"
    "    body: |-\n" + "      段落\n" * 28 + "      ```mermaid\n"
    "      flowchart TD\n"
    "        subgraph S\n"
    "        A\n"
    "      ```\n"
)


def test_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fake_maid_factory: FakeMaidFactory,
    stdin_factory: Callable[[str], None],
) -> None:
    """違反の無い文書（正常系）。"""
    # 準備
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)
    maid = fake_maid_factory()
    monkeypatch.setattr(knowledge_checks, "find_maid", lambda: maid)
    stdin_factory(_VALID_DOC)
    # 実行
    code = knowledge_checks.main([])
    # 検証
    assert code == 0
    assert json.loads(capsys.readouterr().out) == []


def test_main_when_maid_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_factory: Callable[[str], None],
) -> None:
    """maid が無い（正常系）。"""
    # 準備
    monkeypatch.setattr(knowledge_checks, "find_maid", lambda: None)
    stdin_factory(_VALID_DOC)
    # 実行
    code = knowledge_checks.main([])
    # 検証
    captured = capsys.readouterr()
    assert code == 2
    assert captured.out == ""
    assert "maid" in captured.err
    assert "環境構築" in captured.err


def test_main_when_unexpected_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fake_maid_factory: FakeMaidFactory,
    stdin_factory: Callable[[str], None],
) -> None:
    """想定していない例外（正常系）。"""
    # 準備
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)
    maid = fake_maid_factory()
    monkeypatch.setattr(knowledge_checks, "find_maid", lambda: maid)

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


def test_check_document(tmp_path: Path, fake_maid_factory: FakeMaidFactory) -> None:
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
        "  - id: z\n"
        "    body: |-\n"
        "      ```mermaid\n"
        "      flowchart TD\n"
        "        subgraph S\n"
        "        A\n"
        "      ```\n"
        "related:\n"
        "  - to: missing\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    stdout = '{"valid": false, "errors": [{"line": 2, "column": 1, "message": "Expected end"}]}'
    maid = fake_maid_factory(stdout=stdout, exit_code=1)
    # 実行
    result = check_document(text, tmp_path, maid, time.monotonic() + 10.0, index={"a": frozenset()})
    # 検証
    assert [v["path"] for v in result] == [
        "items[1].id",
        "items[2].body",
        "related[0].to",
        "items[3].body",
    ]


def test_check_document_when_broken(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """読めない YAML（正常系）。"""
    # 準備
    calls: list[Path] = []

    def _spy_index(root: Path) -> dict[str, frozenset[str]]:
        calls.append(root)
        return {}

    monkeypatch.setattr(knowledge_checks, "build_id_index", _spy_index)
    # 呼ばれないことを確かめるため、無い maid のパスを渡す
    record = tmp_path / "maid-called"
    # 実行
    result = check_document(
        "items:\n  - id: a\n    name: [\n", tmp_path, str(record), time.monotonic() + 10.0
    )
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "$"
    assert "行目: YAML として読めません" in result[0]["rule"]
    assert calls == []
    assert not record.exists()


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


def test_mermaid_blocks() -> None:
    """mermaid のブロックだけを取り出す（正常系）。"""
    # 準備
    text = "段落\n\n```mermaid\nflowchart TD\n  A --> B\n```\n\n```python\nprint(1)\n```"
    # 実行
    result = mermaid_blocks(text)
    # 検証
    assert result == [(3, "flowchart TD\n  A --> B")]


def test_mermaid_blocks_when_nested_in_example() -> None:
    """4 つ以上の囲みの中は見ない（正常系）。"""
    # 準備
    text = "````markdown\n```mermaid\nflowchart TD\n  A --> B\n```\n````"
    # 実行
    result = mermaid_blocks(text)
    # 検証
    assert result == []


def test_mermaid_blocks_when_unclosed() -> None:
    """閉じ忘れ（正常系）。"""
    # 準備
    text = "```mermaid\nflowchart TD\n  A --> B"
    # 実行
    result = mermaid_blocks(text)
    # 検証
    assert result == [(1, "flowchart TD\n  A --> B")]


def test_check_mermaid(fake_maid_factory: FakeMaidFactory) -> None:
    """誤りを文書の行に戻す（正常系）。"""
    # 準備
    doc = load_document(_MERMAID_AT_40)
    stdout = '{"valid": false, "errors": [{"line": 3, "column": 1, "message": "Expected end"}]}'
    maid = fake_maid_factory(stdout=stdout, exit_code=1)
    # 実行
    result = check_mermaid(doc, maid, time.monotonic() + 10.0)
    # 検証
    assert len(result) == 1
    assert result[0]["path"] == "items[3].body"
    assert result[0]["rule"].startswith("42 行目: mermaid: ")


def test_check_mermaid_when_no_time_left(
    tmp_path: Path, fake_maid_factory: FakeMaidFactory
) -> None:
    """残り時間が足りない（正常系）。"""
    # 準備
    doc = load_document(_MERMAID_AT_40)
    record = tmp_path / "called.jsonl"
    maid = fake_maid_factory(record=record)
    # 実行
    result = check_mermaid(doc, maid, time.monotonic() + 0.5)
    # 検証
    assert len(result) == 1
    assert "処理時間の上限に達したため検査していません" in result[0]["rule"]
    assert not record.exists()


def test_check_mermaid_when_timeout(fake_maid_factory: FakeMaidFactory) -> None:
    """maid を打ち切った（正常系）。"""
    # 準備
    doc = load_document(_MERMAID_AT_40)
    maid = fake_maid_factory(sleep_sec=5.0)
    started = time.monotonic()
    # 実行
    result = check_mermaid(doc, maid, started + 1.5)
    # 検証
    assert time.monotonic() - started < 2.5
    assert len(result) == 1
    assert "処理時間の上限に達したため検査していません" in result[0]["rule"]


def test_check_mermaid_when_bad_output(fake_maid_factory: FakeMaidFactory) -> None:
    """maid の出力が読めない（正常系）。"""
    # 準備
    doc = load_document(_MERMAID_AT_40)
    maid = fake_maid_factory(stdout="ok", exit_code=0)
    # 実行
    result = check_mermaid(doc, maid, time.monotonic() + 10.0)
    # 検証
    assert len(result) == 1
    assert result[0]["fix"] == "開発コマンドの環境構築で入れた maid のバージョンを確かめる"
