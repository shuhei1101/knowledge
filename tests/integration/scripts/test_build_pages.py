"""Pages の成果物の作成（scripts/build_pages.py）の結合テスト。"""

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]
type RepoFactory = Callable[[dict[str, str]], Path]

# 本物の変換のスクリプトを呼ぶ変換のコマンド。一時フォルダから、リポジトリのスクリプトを絶対パスで呼ぶ
_CONVERTER_RUN = [
    "uv",
    "run",
    "--frozen",
    "--script",
    str(Path(__file__).resolve().parents[3] / "scripts" / "knowledge_markdown.py"),
]

# 標準エラーに 1 行出して終了コード 1 で終わる変換のコマンド
_FAILING_RUN = [
    sys.executable,
    "-c",
    "import sys; sys.stdin.read(); sys.stderr.write('converter broken\\n'); sys.exit(1)",
]

# 標準エラーに 1 行出して終了コード 1 で終わる npx の差し替え
_FAILING_NPX = (
    f"#!{sys.executable}\nimport sys\nsys.stderr.write('mdmark broken\\n')\nsys.exit(1)\n"
)

# 公開の文書 a。b の項目と、internal の文書 c を参照する
_DOC_A = (
    "id: a\n"
    "kind: rule\n"
    "name: 文書 A\n"
    "description: A の文書\n"
    "visibility: public\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: 公開 A の本文\n"
    "  - id: link\n"
    "    name: 参照\n"
    "    body: '[B の手順](id:b#step) と [C](id:c#step)'\n"
)

# 公開の文書 b
_DOC_B = (
    "id: b\n"
    "kind: rule\n"
    "name: 文書 B\n"
    "description: B の文書\n"
    "visibility: public\n"
    "items:\n"
    "  - id: step\n"
    "    name: 手順\n"
    "    body: 公開 B の本文\n"
)

# internal の文書 c
_DOC_C = (
    "id: c\n"
    "kind: rule\n"
    "name: 文書 C\n"
    "description: C の文書\n"
    "visibility: internal\n"
    "items:\n"
    "  - id: step\n"
    "    name: 手順\n"
    "    body: 非公開 C の本文\n"
)

# documents[] にどの文書も無い ID を参照する公開の文書 a
_DOC_A_MISSING = (
    "id: a\n"
    "kind: rule\n"
    "name: 文書 A\n"
    "description: A の文書\n"
    "visibility: public\n"
    "items:\n"
    "  - id: link\n"
    "    name: 参照\n"
    "    body: '[無い文書](id:missing)'\n"
)


def _dev_docs(run: list[str]) -> str:
    """docs/rule/ の文書を、渡したコマンドで変換する dev-docs.yaml を返す。"""
    # run は JSON の配列で書く（JSON は YAML として読める）
    return (
        'version: "3"\n'
        "name: knowledge\n"
        "converters:\n"
        "  - id: knowledge-markdown\n"
        f"    run: {json.dumps(run)}\n"
        "documents:\n"
        "  - id: rule\n"
        "    paths:\n"
        "      - docs/rule/*.yaml\n"
        "    schema: schemas/rule.schema.yaml\n"
        "    converter: knowledge-markdown\n"
    )


def test_normal(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """公開の文書だけを 1 枚の HTML にまとめ、終了コード 0 で終わる（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "dev-docs.yaml": _dev_docs(_CONVERTER_RUN),
            "docs/rule/a.yaml": _DOC_A,
            "docs/rule/b.yaml": _DOC_B,
            "docs/rule/c.yaml": _DOC_C,
        }
    )
    # 実行
    result = run_script("build_pages", root, args=["--out", "_site"])
    # 検証
    html = (root / "_site" / "index.html").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert sorted(path.name for path in (root / "_site").iterdir()) == ["index.html"]
    assert "公開 A の本文" in html
    assert "公開 B の本文" in html
    assert "非公開 C の本文" not in html
    assert "(./b.md#手順)" in html
    assert "(https://github.com/shuhei1101/knowledge/blob/master/docs/rule/c.yaml)" in html


def test_error_when_converter_fails(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """変換のスクリプトが失敗した文書で止め、出力を残さずに終わる（異常系）。"""
    # 準備
    root = repo_factory(
        {
            "dev-docs.yaml": _dev_docs(_FAILING_RUN),
            "docs/rule/a.yaml": _DOC_A,
            "docs/rule/b.yaml": _DOC_B,
            "docs/rule/c.yaml": _DOC_C,
        }
    )
    # 実行
    result = run_script("build_pages", root, args=["--out", "_site"])
    # 検証
    assert result.exit_code == 1
    assert "docs/rule/a.yaml" in result.stderr
    assert "converter broken" in result.stderr
    assert not (root / "_site" / "index.html").exists()


def test_error_when_reference_missing(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """documents に無い ID への参照があれば、出力を残さずに終わる（異常系）。"""
    # 準備
    root = repo_factory(
        {
            "dev-docs.yaml": _dev_docs(_CONVERTER_RUN),
            "docs/rule/a.yaml": _DOC_A_MISSING,
        }
    )
    # 実行
    result = run_script("build_pages", root, args=["--out", "_site"])
    # 検証
    assert result.exit_code == 1
    assert "docs/rule/a.yaml" in result.stderr
    assert "missing" in result.stderr
    assert not (root / "_site" / "index.html").exists()


def test_error_when_mdmark_fails(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """mdmark の build が失敗すれば、出力を残さずに終わる（異常系）。"""
    # 準備
    root = repo_factory(
        {
            "dev-docs.yaml": _dev_docs(_CONVERTER_RUN),
            "docs/rule/a.yaml": _DOC_A,
            "docs/rule/b.yaml": _DOC_B,
            "docs/rule/c.yaml": _DOC_C,
        }
    )
    npx_dir = tmp_path / "npx-bin"
    npx_dir.mkdir()
    npx = npx_dir / "npx"
    npx.write_text(_FAILING_NPX, encoding="utf-8")
    npx.chmod(0o755)
    # 実行
    result = run_script("build_pages", root, args=["--out", "_site"], path_prefix=npx_dir)
    # 検証
    assert result.exit_code == 1
    assert "mdmark broken" in result.stderr
    assert not (root / "_site" / "index.html").exists()


def test_error_when_no_public(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """公開の文書が 0 件なら成果物を作り始めずに終わる（異常系）。"""
    # 準備
    root = repo_factory(
        {
            "dev-docs.yaml": _dev_docs(_CONVERTER_RUN),
            "docs/rule/c.yaml": _DOC_C,
        }
    )
    # 実行
    result = run_script("build_pages", root, args=["--out", "_site"])
    # 検証
    assert result.exit_code == 2
    assert "visibility: public の文書がありません" in result.stderr


def test_error_when_config_missing(run_script: RunScript, tmp_path: Path) -> None:
    """dev-docs.yaml が無いか読めなければ成果物を作り始めずに終わる（異常系）。"""
    # 準備
    root = tmp_path / "empty"
    root.mkdir()
    # 実行
    result = run_script("build_pages", root, args=["--out", "_site"])
    # 検証
    assert result.exit_code == 2
    assert "dev-docs.yaml がありません" in result.stderr
