"""文書の違反の検査（scripts/knowledge_checks.py）の結合テスト。"""

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]
type RepoFactory = Callable[[dict[str, str]], Path]

# 項目 x を持つ配信元の文書
_DOC_A = "id: a\nkind: rule\nname: A\ndescription: A の文書\nitems:\n  - id: x\n    name: X\n    body: 本文\n"


def _hashes(root: Path) -> dict[str, str]:
    """フォルダの配下の全てのファイルのハッシュを返す。"""
    return {
        str(file.relative_to(root)): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in sorted(root.rglob("*"))
        if file.is_file()
    }


def test_normal(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """違反の無い文書に空の配列を返す（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/a.yaml": _DOC_A})
    before = _hashes(root)
    stdin = (
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: |-\n"
        "      [A](id:a#x)\n"
        "related:\n"
        "  - to: a\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []
    assert _hashes(root) == before


def test_normal_when_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """項目の ID の重複・参照切れを全て配列で返す（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/a.yaml": _DOC_A})
    stdin = (
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: 本文\n"
        "  - id: p\n"
        "    body: 本文\n"
        "  - id: q\n"
        "    body: '[B](id:missing)'\n"
        "related:\n"
        "  - to: missing\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [v["path"] for v in violations] == [
        "items[1].id",
        "items[2].body",
        "related[0].to",
    ]


def test_normal_when_word_list_examples_fail(
    run_script: RunScript, repo_factory: RepoFactory
) -> None:
    """対応表の行の examples が照合と合わなければ、1 件 1 違反で返す（正常系）。"""
    # 準備
    root = repo_factory({})
    (root / "docs" / "word-list").mkdir()
    stdin = (
        "id: self\n"
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
    lines = stdin.splitlines()
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert [violation["path"] for violation in violations] == [
        "entries[0].examples.hit[0]",
        "entries[1].examples.pass[0]",
        "entries[2].pattern",
    ]
    # rule の先頭の行番号が、文書の中の該当する行を指す
    for violation, text in zip(violations, ["直した", "形式", "形("], strict=True):
        number = int(violation["rule"].split(" 行目")[0])
        assert text in lines[number - 1]


# docs/rule/*.yaml の行が alias_type を持ち、docs/word-list/*.yaml の行は持たない project-index.yaml
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


def test_normal_when_aliases_collide(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """ほかの文書の name・aliases と正規化して一致する aliases を、1 件 1 違反で返す（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "project-index.yaml": _ALIAS_CONFIG,
            "docs/rule/a.yaml": "id: a\nname: Alpha 規約\naliases:\n  - アルファ\n",
            # 書き込む前の b
            "docs/rule/b.yaml": "id: b\nname: B\naliases:\n  - ベータ\n",
            "docs/word-list/w.yaml": "id: w\nname: 単語表\n",
        }
    )
    stdin = (
        "id: b\nname: B\naliases:\n  - ' ａｌｐｈａ 規約 '\n  - アルファ\n  - ベータ\n  - 単語表\n"
    )
    lines = stdin.splitlines()
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert [violation["path"] for violation in violations] == ["aliases[0]", "aliases[1]"]
    assert "`a` の name" in violations[0]["rule"]
    assert "`a` の aliases" in violations[1]["rule"]
    # rule の先頭の行番号が、文書の中の該当する行を指す
    for violation, text in zip(violations, ["ａｌｐｈａ", "アルファ"], strict=True):
        number = int(violation["rule"].split(" 行目")[0])
        assert text in lines[number - 1]


# 規約の行（alias_type: doc）と用語集の行（records: terms・alias_type: term）を持つ project-index.yaml
_TERMS_CONFIG = (
    'version: "3"\n'
    "name: knowledge\n"
    "documents:\n"
    "  - id: rule\n"
    "    paths: [docs/rule/*.yaml]\n"
    "    alias_type: doc\n"
    "  - id: terms\n"
    "    paths: [docs/terms.yaml]\n"
    "    records: terms\n"
    "    alias_type: term\n"
)


def test_normal_when_aliases_collide_with_terms(
    run_script: RunScript, repo_factory: RepoFactory
) -> None:
    """records を持つ行の文書は、要素ごとの name・aliases を照合の相手にする（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "project-index.yaml": _TERMS_CONFIG,
            "docs/terms.yaml": (
                "id: terms\n"
                "name: 用語集\n"
                "terms:\n"
                "  - id: ai-slop\n"
                "    name: AI slop\n"
                "    aliases:\n"
                "      - AI らしい単語\n"
            ),
        }
    )
    stdin = "id: b\nname: B\naliases:\n  - AI らしい単語\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert [violation["path"] for violation in violations] == ["aliases[0]"]
    assert "`ai-slop` の aliases" in violations[0]["rule"]


def test_normal_when_aliases_duplicate(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """自分の name か前の aliases と正規化して一致する aliases を、1 件 1 違反で返す（正常系）。"""
    # 準備
    root = repo_factory({"project-index.yaml": _ALIAS_CONFIG, "docs/rule/a.yaml": _DOC_A})
    stdin = "id: b\nname: Beta 規約\naliases:\n  - ベータ\n  - ' ｂｅｔａ 規約 '\n  - べーた\n  - ' ベータ '\n"
    lines = stdin.splitlines()
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert [violation["path"] for violation in violations] == ["aliases[1]", "aliases[3]"]
    assert "name" in violations[0]["rule"]
    assert "aliases[0]" in violations[1]["rule"]
    # rule の先頭の行番号が、文書の中の該当する行を指す
    assert violations[0]["rule"].startswith("5 行目: ")
    assert "ｂｅｔａ 規約" in lines[4]
    assert violations[1]["rule"].startswith("7 行目: ")
    assert " ベータ " in lines[6]


def test_normal_when_config_missing(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """project-index.yaml が無ければ aliases を照合せず、path: $ の違反とほかの検査の違反を返す（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/a.yaml": _DOC_A})
    (root / "project-index.yaml").unlink()
    stdin = "id: self\naliases:\n  - アルファ\nitems:\n  - id: p\n    body: '[B](id:missing)'\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert sorted(violation["path"] for violation in violations) == ["$", "items[0].body"]
    config = next(violation for violation in violations if violation["path"] == "$")
    assert "project-index.yaml" in config["rule"]


def test_normal_when_invalid_yaml(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """読めない入力を path: $ の違反 1 件で返す（正常系）。"""
    # 準備
    root = repo_factory({})
    stdin = "items:\n  - id: a\n    name: [\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert len(violations) == 1
    assert violations[0]["path"] == "$"
    assert " 行目: " in violations[0]["rule"]
