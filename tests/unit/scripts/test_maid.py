"""scripts/_maid.py の単体テスト。"""

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from _maid import MaidFinding, MaidOutputError, find_maid, run_maid

type FakeMaidFactory = Callable[..., str]


def test_find_maid(monkeypatch: pytest.MonkeyPatch, fake_maid_factory: FakeMaidFactory) -> None:
    """PATH にある maid を引く（正常系）。"""
    # 準備
    maid = fake_maid_factory()
    monkeypatch.setenv("PATH", str(Path(maid).parent))
    # 実行
    result = find_maid()
    # 検証
    assert result == maid


def test_find_maid_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """PATH に無い（正常系）。"""
    # 準備
    empty = tmp_path / "empty-bin"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    # 実行
    result = find_maid()
    # 検証
    assert result is None


def test_run_maid(tmp_path: Path, fake_maid_factory: FakeMaidFactory) -> None:
    """正しい図（正常系）。"""
    # 準備
    record = tmp_path / "args.jsonl"
    maid = fake_maid_factory(stdout='{"valid": true, "errors": []}', exit_code=0, record=record)
    # 実行
    result = run_maid(maid, "flowchart TD\n  A --> B", 10.0)
    # 検証
    assert result == []
    assert json.loads(record.read_text(encoding="utf-8")) == ["-", "--format", "json"]


def test_run_maid_when_invalid(fake_maid_factory: FakeMaidFactory) -> None:
    """誤った図（正常系）。"""
    # 準備
    stdout = '{"valid": false, "errors": [{"line": 3, "column": 1, "message": "Expected end"}]}'
    maid = fake_maid_factory(stdout=stdout, exit_code=1)
    # 実行
    result = run_maid(maid, "flowchart TD\n  subgraph S\n  A", 10.0)
    # 検証
    assert result == [MaidFinding(line=3, message="Expected end")]


def test_run_maid_when_crashed(fake_maid_factory: FakeMaidFactory) -> None:
    """maid が落ちた（異常系）。"""
    # 準備
    maid = fake_maid_factory(stdout="", exit_code=2, stderr="TypeError: boom\n")
    # 実行・検証
    with pytest.raises(MaidOutputError, match=r"終了コード 2.*TypeError: boom"):
        run_maid(maid, "flowchart TD\n  A --> B", 10.0)


def test_run_maid_when_not_json(fake_maid_factory: FakeMaidFactory) -> None:
    """出力が JSON でない（異常系）。"""
    # 準備
    maid = fake_maid_factory(stdout="ok", exit_code=0)
    # 実行・検証
    with pytest.raises(MaidOutputError, match="maid の出力を読めません"):
        run_maid(maid, "flowchart TD\n  A --> B", 10.0)
