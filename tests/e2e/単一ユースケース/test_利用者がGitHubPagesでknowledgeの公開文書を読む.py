"""利用者が GitHub Pages で knowledge の公開文書を読む（SC-137-1）の E2E テスト。"""

import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from ruamel.yaml import YAML

# conftest の fixture の型。子プロセスの結果は subprocess.CompletedProcess
type KnowledgeClone = Callable[..., Path]
type RunCommand = Callable[[Path], Any]

# リポジトリの直下
_REPO_ROOT = Path(__file__).resolve().parents[3]

# 参照を足す公開の文書の元にする、公開の使い方
_SOURCE = _REPO_ROOT / "docs" / "guide" / "guide-setup-install-plugin.yaml"
# 公開の文書と internal の文書を 1 つずつ参照する公開の文書
_REFERRING = "docs/guide/e2e-pages-reference.yaml"
# 参照先の internal の文書と、その本文にだけある文字
_INTERNAL_ID = "dev-yaml"
_INTERNAL_TEXT = "main_repo_root"

# 成果物の HTML に埋め込まれた mdmark の文書の一覧
_PAYLOAD = re.compile(
    r'<script type="application/json" id="mdmark-payload">(.*?)</script>', re.DOTALL
)

# 変換のコマンドの行と、標準エラーに 1 行出して終了コード 1 で終わる変換のコマンド
_CONVERTER_RUN = "    run: [uv, run, --frozen, --script, scripts/knowledge_markdown.py]"
_FAILING_RUN = [
    sys.executable,
    "-c",
    "import sys; sys.stdin.read(); sys.stderr.write('converter broken\\n'); sys.exit(1)",
]

# 出力のフォルダに混ぜる YAML
_MIXED_YAML = "_site/e2e-mixed.yaml"


def _referring_document() -> dict[str, str]:
    """公開の文書の項目と internal の文書を参照する公開の文書を返す。"""
    source = _SOURCE.read_text(encoding="utf-8")
    text = source.replace("id: guide-setup-install-plugin", "id: e2e-pages-reference", 1)
    text += (
        "  - id: e2e-reference\n"
        "    name: 参照\n"
        f"    body: '[元に戻す](id:guide-setup-install-plugin#rollback-01) と [YAML](id:{_INTERNAL_ID}#overview)'\n"
    )
    return {_REFERRING: text}


def _failing_converter() -> dict[str, str]:
    """変換のコマンドを、終了コード 1 で終わるものに差し替えた dev-docs.yaml を返す。"""
    config = (_REPO_ROOT / "dev-docs.yaml").read_text(encoding="utf-8")
    return {
        "dev-docs.yaml": config.replace(_CONVERTER_RUN, f"    run: {json.dumps(_FAILING_RUN)}", 1)
    }


def _load(path: Path) -> dict[str, Any]:
    """YAML のファイルを読んだ値を返す。"""
    return cast("dict[str, Any]", YAML(typ="safe").load(path.read_text(encoding="utf-8")))  # pyright: ignore[reportUnknownMemberType]


def _public_markdowns(clone: Path) -> set[str]:
    """クローンの converter を持つ documents[] の行の文書のうち、公開の文書の `{id}.md` を返す。"""
    names: set[str] = set()
    for row in _load(clone / "dev-docs.yaml")["documents"]:
        # records の行と変換しない行は成果物に入らない
        if "records" in row or "converter" not in row:
            continue
        for pattern in row["paths"]:
            for file in clone.glob(pattern):
                doc = _load(file)
                if doc.get("visibility") == "public":
                    names.add(f"{doc['id']}.md")
    return names


def _bundled_docs(clone: Path) -> dict[str, str]:
    """成果物の HTML に埋め込まれた文書の、`{id}.md` → Markdown を返す。"""
    html = (clone / "_site" / "index.html").read_text(encoding="utf-8")
    matched = _PAYLOAD.search(html)
    assert matched is not None
    payload = cast("dict[str, Any]", json.loads(matched.group(1)))
    return {str(doc["path"]): str(doc["markdown"]) for doc in payload["docs"]}


def test_normal(
    knowledge_clone: KnowledgeClone,
    run_pages_build: RunCommand,
    run_pages_yaml_check: RunCommand,
) -> None:
    """公開の文書だけを HTML にし、YAML の無い成果物を作る（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone(_referring_document())
    # 実行
    built = run_pages_build(clone)
    checked = run_pages_yaml_check(clone)
    # 検証
    docs = _bundled_docs(clone)
    referring = docs["e2e-pages-reference.md"]
    assert built.returncode == 0, built.stderr
    assert checked.returncode == 0
    assert checked.stdout == ""
    assert sorted(path.name for path in (clone / "_site").iterdir()) == ["index.html"]
    assert set(docs) == _public_markdowns(clone)
    assert f"{_INTERNAL_ID}.md" not in docs
    assert _INTERNAL_TEXT not in "".join(docs.values())
    assert re.search(r"\]\(\./guide-setup-install-plugin\.md#[^)]+\)", referring)
    assert (
        f"](https://github.com/shuhei1101/knowledge/blob/master/docs/rule/{_INTERNAL_ID}.yaml)"
        in referring
    )


def test_error_when_converter_fails(
    knowledge_clone: KnowledgeClone, run_pages_build: RunCommand
) -> None:
    """変換のスクリプトが失敗すれば、配信へ進まずに失敗する（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone(_failing_converter())
    # 実行
    built = run_pages_build(clone)
    # 検証
    assert built.returncode == 1
    assert re.search(r"docs/\S+\.yaml: 変換のスクリプトが終了コード 1 で失敗しました", built.stderr)
    assert "converter broken" in built.stderr
    assert not (clone / "_site" / "index.html").exists()


def test_error_when_output_contains_yaml(
    knowledge_clone: KnowledgeClone,
    run_pages_build: RunCommand,
    run_pages_yaml_check: RunCommand,
) -> None:
    """出力のフォルダに YAML が混じれば、そのパスを出して配信へ進まずに失敗する（異常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    built = run_pages_build(clone)
    (clone / _MIXED_YAML).write_text("id: mixed\n", encoding="utf-8")
    # 実行
    checked = run_pages_yaml_check(clone)
    # 検証
    assert built.returncode == 0, built.stderr
    assert checked.returncode == 1
    assert checked.stdout.splitlines() == [_MIXED_YAML]
