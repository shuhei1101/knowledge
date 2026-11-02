"""利用者が画面で knowledge の文書を読む（SC-72-3）の E2E テスト。"""

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from ruamel.yaml import YAML

# conftest の fixture の型。起動した dev-docs は conftest の Served
type KnowledgeClone = Callable[..., Path]
type Serve = Callable[..., Any]
type KnowledgeRow = Callable[..., Any]
type RepresentativePages = Callable[[Path], dict[str, str]]

# リポジトリの直下
_ROOT = Path(__file__).resolve().parents[3]
# 変換のスクリプトの PEP 723 のヘッダー（`# ///` で閉じるまで）
_HEADER = re.compile(r"\A.*?^# ///$\n", re.MULTILINE | re.DOTALL)
# 終了コード 1 で終わる変換のスクリプトの本体
_FAILING_BODY = 'import sys\n\nprint("変換に失敗しました", file=sys.stderr)\nsys.exit(1)\n'
# 変換を通さず本文を出す files.yaml の行のページ
_SKILL_PAGE = "skills/files/skills/text-review/SKILL"


def _load(file: Path) -> dict[str, Any]:
    """YAML のファイルを読んだ値を返す。"""
    return cast("dict[str, Any]", YAML(typ="safe").load(file.read_text(encoding="utf-8")))


def _document_pages(clone: Path, document: dict[str, Any]) -> list[str]:
    """文書の行が持つ全てのページの path を、path の順に返す。"""
    files = [file for pattern in document["paths"] for file in clone.glob(pattern)]
    # files.yaml の行の文書は、行ごとのファイルがページになる
    if "records" in document:
        paths = [
            f"{file.relative_to(clone).with_suffix('')}/{(file.parent / str(record[document['body_file']])).relative_to(clone).with_suffix('')}"
            for file in files
            for record in _load(file)[document["records"]]
        ]
    else:
        paths = [str(file.relative_to(clone).with_suffix("")) for file in files]
    return sorted(paths)


def _expected_items(clone: Path, items: list[dict[str, Any]]) -> list[Any]:
    """`nav` の行から、サイドバーに並ぶはずの group のタイトルとページの path を組み立てる。"""
    documents = {
        document["id"]: document for document in _load(clone / "dev-docs.yaml")["documents"]
    }
    expected: list[Any] = []
    for item in items:
        # 文書の行を展開する行・1 ページの行・group の行で分ける
        if "auto" in item:
            expected += _document_pages(clone, documents[item["auto"]["document"]])
        elif "page" in item:
            expected.append(f"docs/{item['page']}")
        else:
            expected.append((item["group"], _expected_items(clone, item["items"])))
    return expected


def _actual_items(items: list[dict[str, Any]]) -> list[Any]:
    """画面の API のサイドバーの行を、group のタイトルとページの path にする。"""
    return [
        (item["title"], _actual_items(item["items"])) if item["kind"] == "group" else item["path"]
        for item in items
    ]


def test_normal(
    knowledge_clone: KnowledgeClone,
    serve: Serve,
    knowledge_row: KnowledgeRow,
    representative_pages: RepresentativePages,
) -> None:
    """全ての種類の文書が開け、タブとサイドバーが nav のとおりに並ぶ（正常シナリオ）。"""
    # 準備
    clone = knowledge_clone()
    served = serve([knowledge_row(clone)])
    nav = _load(clone / "dev-docs.yaml")["nav"]["tabs"]
    # 実行
    pages = {
        kind: served.open_page("knowledge", path)
        for kind, path in representative_pages(clone).items()
    }
    tabs = served.open_page("knowledge").body["tabs"]
    # 検証
    assert {kind: page.status for kind, page in pages.items()} == dict.fromkeys(pages, 200)
    assert [kind for kind, page in pages.items() if not page.body["markdown"].strip()] == []
    assert [tab["title"] for tab in tabs] == [tab["title"] for tab in nav]
    assert [_actual_items(tab["items"]) for tab in tabs] == [
        _expected_items(clone, tab["items"]) for tab in nav
    ]


def test_error_when_converter_fails(
    knowledge_clone: KnowledgeClone, serve: Serve, knowledge_row: KnowledgeRow
) -> None:
    """変換に失敗した文書は失敗の理由を出し、files.yaml の行の文書は開ける（異常シナリオ）。"""
    # 準備
    script = (_ROOT / "scripts" / "knowledge_markdown.py").read_text(encoding="utf-8")
    header = _HEADER.match(script)
    assert header is not None
    clone = knowledge_clone({"scripts/knowledge_markdown.py": header.group(0) + _FAILING_BODY})
    served = serve([knowledge_row(clone)])
    # 実行
    rule = served.open_page("knowledge", "docs/rule/dev-precheck")
    skill = served.open_page("knowledge", _SKILL_PAGE)
    # 検証
    assert rule.status == 200
    assert rule.body["conversionError"]["reason"] == "exit"
    assert "変換に失敗しました" in rule.body["conversionError"]["detail"]
    assert skill.status == 200
    assert skill.body["conversionError"] is None
    assert skill.body["markdown"] == (clone / "skills" / "text-review" / "SKILL.md").read_text(
        encoding="utf-8"
    )
