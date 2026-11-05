"""scripts/build_pages.py の単体テスト。"""

import json
import sys
from collections.abc import Callable
from pathlib import Path, PurePosixPath
from typing import Any

import pytest

import build_pages
from build_pages import (
    BuildError,
    Source,
    convert_source,
    github_slug,
    item_anchors,
    list_sources,
    load_converters,
    rewrite_references,
    run_mdmark,
    write_bundle_config,
)

# 公開の文書を変換の行で引く dev-docs.yaml
_DEV_DOCS_YAML = (
    'version: "3"\n'
    "name: knowledge\n"
    "converters:\n"
    "  - id: knowledge-markdown\n"
    "    run: [uv, run, --frozen, --script, scripts/knowledge_markdown.py]\n"
    "documents:\n"
    "  - id: guide\n"
    '    paths: ["docs/guide/*.yaml"]\n'
    "    schema: schemas/guide.schema.yaml\n"
    "    converter: knowledge-markdown\n"
    "  - id: scripts\n"
    "    paths: [scripts/files.yaml]\n"
    "    schema: schemas/files.schema.yaml\n"
    "    records: files\n"
)


def _document(doc_id: str, visibility: str) -> str:
    """概要と手順の項目を持つ文書の YAML を返す。"""
    return (
        f"id: {doc_id}\n"
        "kind: guide\n"
        f"name: {doc_id}\n"
        "description: 説明\n"
        f"visibility: {visibility}\n"
        "items:\n"
        "  - id: overview\n"
        "    name: 概要\n"
        "    body: 本文\n"
        "  - id: step\n"
        "    name: 手順\n"
        "    body: 本文\n"
    )


type RepoWriter = Callable[[dict[str, str]], Path]


@pytest.fixture
def repo_writer(tmp_path: Path) -> RepoWriter:
    """渡したファイルを持つリポジトリの直下を作る関数を返す。"""

    def _create(files: dict[str, str]) -> Path:
        root = tmp_path / "repo"
        root.mkdir()
        for relative, text in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    return _create


@pytest.fixture
def fake_mdmark(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """mdmark の build の呼び出しを、設定の build.out に HTML を書くものに差し替え、読んだ設定の記録を返す。"""
    configs: list[dict[str, Any]] = []

    def _run(config: Path) -> str:
        loaded: dict[str, Any] = json.loads(config.read_text(encoding="utf-8"))
        configs.append(loaded)
        (config.parent / loaded["build"]["out"]).write_text("<html></html>", encoding="utf-8")
        return "書き出した: index.html（文書 2 件）"

    monkeypatch.setattr(build_pages, "run_mdmark", _run)
    return configs


def test_main(
    monkeypatch: pytest.MonkeyPatch,
    repo_writer: RepoWriter,
    fake_mdmark: list[dict[str, Any]],
) -> None:
    """公開の文書だけをまとめる（正常系）。"""
    # 準備
    root = repo_writer(
        {
            "dev-docs.yaml": _DEV_DOCS_YAML,
            "docs/guide/guide-a.yaml": _document("guide-a", "public"),
            "docs/guide/guide-b.yaml": _document("guide-b", "public"),
            "docs/guide/guide-c.yaml": _document("guide-c", "internal"),
            "scripts/files.yaml": "files: []\n",
            "_site/old.html": "<html></html>",
        }
    )
    monkeypatch.chdir(root)

    def _convert(_root: Path, source: Source) -> str:
        return f"# {source.id}\n"

    monkeypatch.setattr(build_pages, "convert_source", _convert)
    # 実行
    code = build_pages.main(["--out", "_site"])
    # 検証
    assert code == 0
    assert sorted(path.name for path in (root / "_site").iterdir()) == ["index.html"]
    assert fake_mdmark[0]["build"]["include"] == ["guide-a.md", "guide-b.md"]


def test_main_when_build_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_writer: RepoWriter,
    fake_mdmark: list[dict[str, Any]],
) -> None:
    """作れない成果物（正常系）。"""
    # 準備
    root = repo_writer(
        {
            "dev-docs.yaml": _DEV_DOCS_YAML,
            "docs/guide/guide-a.yaml": _document("guide-a", "public"),
            "docs/guide/guide-b.yaml": _document("guide-b", "public"),
            "docs/guide/guide-c.yaml": _document("guide-c", "internal"),
            "scripts/files.yaml": "files: []\n",
            "_site/index.html": "<html></html>",
        }
    )
    monkeypatch.chdir(root)

    def _fail(_root: Path, source: Source) -> str:
        message = f"{source.path}: 変換のスクリプトが終了コード 1 で失敗しました"
        raise BuildError(message)

    monkeypatch.setattr(build_pages, "convert_source", _fail)
    # 実行
    code = build_pages.main(["--out", "_site"])
    # 検証
    assert code == 1
    assert "変換のスクリプトが終了コード 1 で失敗しました" in capsys.readouterr().err
    assert list((root / "_site").iterdir()) == []
    assert fake_mdmark == []


def test_main_when_no_public(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_writer: RepoWriter,
) -> None:
    """公開の文書が無い（正常系）。"""
    # 準備
    root = repo_writer(
        {
            "dev-docs.yaml": _DEV_DOCS_YAML,
            "docs/guide/guide-c.yaml": _document("guide-c", "internal"),
        }
    )
    monkeypatch.chdir(root)
    # 実行
    code = build_pages.main(["--out", "_site"])
    # 検証
    assert code == 2
    assert "visibility: public" in capsys.readouterr().err


def test_main_when_config_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """dev-docs.yaml が無い（正常系）。"""
    # 準備
    monkeypatch.chdir(tmp_path)
    # 実行
    code = build_pages.main(["--out", "_site"])
    # 検証
    assert code == 2
    assert "dev-docs.yaml" in capsys.readouterr().err


def test_load_converters(tmp_path: Path) -> None:
    """変換のコマンドを引く（正常系）。"""
    # 準備
    (tmp_path / "dev-docs.yaml").write_text(_DEV_DOCS_YAML, encoding="utf-8")
    # 実行
    result = load_converters(tmp_path)
    # 検証
    assert result == {
        "knowledge-markdown": (
            "uv",
            "run",
            "--frozen",
            "--script",
            "scripts/knowledge_markdown.py",
        )
    }


def test_list_sources(repo_writer: RepoWriter) -> None:
    """変換の行の文書を読む（正常系）。"""
    # 準備
    root = repo_writer(
        {
            "docs/guide/guide-a.yaml": _document("guide-a", "public"),
            "docs/guide/guide-b.yaml": _document("guide-b", "internal"),
            "scripts/files.yaml": "files: []\n",
        }
    )
    rows = [
        {
            "id": "guide",
            "paths": ["docs/guide/*.yaml"],
            "schema": "schemas/guide.schema.yaml",
            "converter": "knowledge-markdown",
        },
        {
            "id": "scripts",
            "paths": ["scripts/files.yaml"],
            "schema": "schemas/files.schema.yaml",
            "records": "files",
        },
    ]
    converters = {"knowledge-markdown": ("uv", "run", "scripts/knowledge_markdown.py")}
    # 実行
    result = list_sources(root, rows, converters)
    # 検証
    assert result == [
        Source(
            id="guide-a",
            path=PurePosixPath("docs/guide/guide-a.yaml"),
            public=True,
            items=(("step", "手順", 2),),
            run=("uv", "run", "scripts/knowledge_markdown.py"),
        ),
        Source(
            id="guide-b",
            path=PurePosixPath("docs/guide/guide-b.yaml"),
            public=False,
            items=(("step", "手順", 2),),
            run=("uv", "run", "scripts/knowledge_markdown.py"),
        ),
    ]


def test_list_sources_when_broken(repo_writer: RepoWriter) -> None:
    """読めない文書（異常系）。"""
    # 準備
    root = repo_writer({"docs/guide/guide-a.yaml": "id: guide-a\nitems: [\n"})
    rows = [{"id": "guide", "paths": ["docs/guide/*.yaml"], "converter": "knowledge-markdown"}]
    converters = {"knowledge-markdown": ("uv", "run", "scripts/knowledge_markdown.py")}
    # 実行・検証
    with pytest.raises(BuildError, match=r"docs/guide/guide-a\.yaml"):
        list_sources(root, rows, converters)


def test_convert_source(tmp_path: Path) -> None:
    """標準出力を返す（正常系）。"""
    # 準備
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.yaml").write_text("id: a\nname: 文書\n", encoding="utf-8")
    source = Source(
        id="a",
        path=PurePosixPath("docs/a.yaml"),
        public=True,
        items=(),
        run=(sys.executable, "-c", "import sys; sys.stdout.write(sys.stdin.read())"),
    )
    # 実行
    result = convert_source(tmp_path, source)
    # 検証
    assert result == "id: a\nname: 文書\n"


def test_convert_source_when_failed(tmp_path: Path) -> None:
    """変換が失敗する（異常系）。"""
    # 準備
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.yaml").write_text("id: a\n", encoding="utf-8")
    source = Source(
        id="a",
        path=PurePosixPath("docs/a.yaml"),
        public=True,
        items=(),
        run=(sys.executable, "-c", "import sys; sys.stderr.write('broken'); sys.exit(1)"),
    )
    # 実行・検証
    with pytest.raises(BuildError, match=r"(?s)docs/a\.yaml.*終了コード 1.*broken"):
        convert_source(tmp_path, source)


def test_convert_source_when_command_missing(tmp_path: Path) -> None:
    """コマンドが無い（異常系）。"""
    # 準備
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.yaml").write_text("id: a\n", encoding="utf-8")
    source = Source(
        id="a",
        path=PurePosixPath("docs/a.yaml"),
        public=True,
        items=(),
        run=("knowledge-no-such-converter",),
    )
    # 実行・検証
    with pytest.raises(BuildError, match="knowledge-no-such-converter"):
        convert_source(tmp_path, source)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("Hello, World!", "hello-world", id="ascii"),
        pytest.param("使い方", "使い方", id="japanese"),
        pytest.param("`uv` で入れる", "uv-で入れる", id="code"),
    ],
)
def test_github_slug(text: str, expected: str) -> None:
    """mdmark の例と同じ ID（正常系）。"""
    # 実行
    result = github_slug(text)
    # 検証
    assert result == expected


def test_item_anchors() -> None:
    """同じ文字の見出しを順に対応づける（正常系）。"""
    # 準備
    markdown = (
        "# 文書\n"
        "\n"
        "## 手順\n"
        "\n"
        "### 手順\n"
        "\n"
        "#123 は Issue の番号\n"
        "\n"
        "```text\n"
        "# 確認\n"
        "```\n"
        "\n"
        "### 確認\n"
        "\n"
        "本文\n"
    )
    items = [("step", "手順", 3), ("check", "確認", 3)]
    # 実行
    result = item_anchors(markdown, items)
    # 検証
    assert result == {"step": "手順-1", "check": "確認"}


def test_rewrite_references() -> None:
    """公開の文書と公開しない文書への参照（正常系）。"""
    # 準備
    public = Source(
        id="pub",
        path=PurePosixPath("docs/guide/pub.yaml"),
        public=True,
        items=(("step", "手順", 2),),
        run=(),
    )
    internal = Source(
        id="int",
        path=PurePosixPath("docs/rule/int.yaml"),
        public=False,
        items=(("step", "手順", 2),),
        run=(),
    )
    markdown = "[a](id:pub) [b](id:pub#step) [c](id:pub#overview) [d](id:int#step)"
    # 実行
    result = rewrite_references(
        markdown, public, {"pub": public, "int": internal}, {"pub": {"step": "手順"}}
    )
    # 検証
    assert result == (
        "[a](./pub.md) [b](./pub.md#手順) [c](./pub.md) "
        "[d](https://github.com/shuhei1101/knowledge/blob/master/docs/rule/int.yaml)"
    )


def test_rewrite_references_when_unknown() -> None:
    """参照先が無い（異常系）。"""
    # 準備
    public = Source(
        id="pub",
        path=PurePosixPath("docs/guide/pub.yaml"),
        public=True,
        items=(),
        run=(),
    )
    # 実行・検証
    with pytest.raises(BuildError, match=r"docs/guide/pub\.yaml.*missing"):
        rewrite_references("[x](id:missing)", public, {"pub": public}, {"pub": {}})


def test_write_bundle_config(tmp_path: Path) -> None:
    """並びのとおりの設定（正常系）。"""
    # 実行
    path = write_bundle_config(tmp_path, ["b.md", "a.md"])
    # 検証
    config = json.loads(path.read_text(encoding="utf-8"))
    assert config["build"]["include"] == ["b.md", "a.md"]
    assert config["build"]["entry"] == "b.md"
    assert config["build"]["out"] == "index.html"


def test_run_mdmark_when_failed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """build が失敗する（異常系）。"""
    # 準備
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    npx = bin_dir / "npx"
    npx.write_text(
        f"#!{sys.executable}\nimport sys\nsys.stderr.write('broken')\nsys.exit(1)\n",
        encoding="utf-8",
    )
    npx.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir))
    config = tmp_path / "work" / "mdmark.config.yaml"
    config.parent.mkdir()
    config.write_text("{}", encoding="utf-8")
    # 実行・検証
    with pytest.raises(BuildError, match=r"(?s)終了コード 1.*broken"):
        run_mdmark(config)


def test_run_mdmark_when_npx_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """npx が無い（異常系）。"""
    # 準備
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    config = tmp_path / "work" / "mdmark.config.yaml"
    config.parent.mkdir()
    config.write_text("{}", encoding="utf-8")
    # 実行・検証
    with pytest.raises(BuildError, match="npx"):
        run_mdmark(config)
