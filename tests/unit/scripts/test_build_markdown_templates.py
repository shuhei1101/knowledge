"""scripts/build_markdown_templates.py の単体テスト。"""

import functools
import json
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import build_markdown_templates
import pytest
from build_markdown_templates import (
    Output,
    TemplateMeta,
    build_outputs,
    build_placeholder,
    list_differences,
    main,
    render_files_index,
    render_markdown,
)
from build_templates import BuildError, load_schemas
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

if TYPE_CHECKING:
    from collections.abc import Mapping

    from conftest import RepoFactory

# リポジトリの直下
_REPO = Path(__file__).resolve().parents[3]

# $ref の解決先を持つ共通のスキーマ
_COMMON = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 共通\n"
    "$defs:\n"
    "  summary:\n"
    "    type: string\n"
    "    title: 概要\n"
)

# enum・真偽・title の無い文字列の配列・入れ子の配列・$ref のキーとトップの examples を持つ種類のスキーマ
_ER = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: ER 図\n"
    "description: データストアの構造をまとめる。\n"
    "x-kind: er\n"
    "type: object\n"
    "properties:\n"
    "  id:\n"
    "    type: string\n"
    "    title: ID\n"
    "  lead:\n"
    "    $ref: common.schema.yaml#/$defs/summary\n"
    "    title: 冒頭リード\n"
    "  kind:\n"
    "    type: string\n"
    "    title: 種別\n"
    "    enum:\n"
    "      - db\n"
    "      - json\n"
    "  draft:\n"
    "    type: boolean\n"
    "    title: 下書き\n"
    "  aliases:\n"
    "    type: array\n"
    "    title: 別名\n"
    "    items:\n"
    "      type: string\n"
    "  tables:\n"
    "    type: array\n"
    "    title: テーブル\n"
    "    items:\n"
    "      type: object\n"
    "      properties:\n"
    "        name:\n"
    "          type: string\n"
    "          title: 物理名\n"
    "examples:\n"
    "  - id: ER-1\n"
    "    tables:\n"
    "      - name: tasks\n"
)

# examples を持たない種類のスキーマ
_CONFIG = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 設定\n"
    "description: 設定値の一覧。\n"
    "x-kind: config\n"
    "type: object\n"
    "properties:\n"
    "  name:\n"
    "    type: string\n"
    "    title: 名前\n"
)

# 対応表に行が無い種類のスキーマ
_INDEX = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 目次\n"
    "description: フォルダの目次。\n"
    "x-kind: index\n"
    "type: object\n"
)

# ER 図の YAML のテンプレート
_TEMPLATE_ER = (
    "id: template-er\n"
    "kind: template\n"
    'name: "テンプレート: ER 図"\n'
    "description: ER 図の書式を定め、ER 図を記載するときに参照する。\n"
    "aliases:\n"
    "  - ER 図のテンプレート\n"
    "tags:\n"
    "  - name: topic:er図\n"
    "    main: true\n"
    "  - name: topic:テンプレート\n"
    "items: []\n"
)

# 設定の YAML のテンプレート
_TEMPLATE_CONFIG = (
    "id: template-config\n"
    "kind: template\n"
    'name: "テンプレート: 設定"\n'
    "description: 設定の書式を定め、設定を記載するときに参照する。\n"
    "tags:\n"
    "  - name: topic:設定\n"
    "items: []\n"
)

# _CONFIG の雛形を _fake_convert で変換した Markdown
_CONFIG_MD = 'config:{"name": "{名前}"}\n'


def _fake_convert(
    kind: str,
    path: PurePosixPath,
    data: Mapping[str, object],
    schema: Mapping[str, object],
) -> str:
    """dev-docs の変換の代わりに、種類と文書を 1 行にした文字列を返却する。"""
    del path, schema
    return f"{kind}:{json.dumps(data, ensure_ascii=False, sort_keys=True)}\n"


# 全ての種類のスキーマと YAML のテンプレートと、config の雛形だけを持つ Markdown のテンプレートのフォルダ
_REPO_FILES = {
    "schemas/design/common.schema.yaml": _COMMON,
    "schemas/design/er.schema.yaml": _ER,
    "schemas/design/config.schema.yaml": _CONFIG,
    "schemas/design/index.schema.yaml": _INDEX,
    "docs/template/template-er.yaml": _TEMPLATE_ER,
    "docs/template/template-config.yaml": _TEMPLATE_CONFIG,
    "docs/template/markdown/config.md": _CONFIG_MD,
}


@pytest.fixture
def fake_build_outputs(monkeypatch: pytest.MonkeyPatch) -> None:
    """main が呼ぶ生成するファイルの組み立てを、dev-docs の変換を差し替えたものにする。"""
    monkeypatch.setattr(
        build_markdown_templates,
        "build_outputs",
        functools.partial(build_outputs, convert=_fake_convert),
    )


@pytest.mark.usefixtures("fake_build_outputs")
def test_main(
    repo_factory: RepoFactory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """ずれた種類だけを書き出す（正常系）。"""
    # 準備
    root = repo_factory(_REPO_FILES)
    monkeypatch.chdir(root)
    # 実行
    code = main([])
    # 検証
    assert code == 0
    assert capsys.readouterr().out == (
        "docs/template/markdown/er.example.md\n"
        "docs/template/markdown/er.md\n"
        "docs/template/markdown/files.yaml\n"
    )
    assert (root / "docs/template/markdown/config.md").read_text(encoding="utf-8") == _CONFIG_MD


@pytest.mark.usefixtures("fake_build_outputs")
def test_main_when_check(
    repo_factory: RepoFactory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--check でずれを出す（正常系）。"""
    # 準備
    root = repo_factory({**_REPO_FILES, "docs/template/markdown/old.md": "# 旧\n"})
    monkeypatch.chdir(root)
    # 実行
    code = main(["--check"])
    # 検証
    assert code == 1
    assert capsys.readouterr().out == (
        "docs/template/markdown/er.example.md\tschemas/design/er.schema.yaml\n"
        "docs/template/markdown/er.md\tschemas/design/er.schema.yaml\n"
        "docs/template/markdown/files.yaml\tschemas/design\n"
        "docs/template/markdown/old.md\n"
    )
    assert sorted(p.name for p in (root / "docs/template/markdown").iterdir()) == [
        "config.md",
        "old.md",
    ]


@pytest.mark.usefixtures("fake_build_outputs")
def test_main_when_unchanged(
    repo_factory: RepoFactory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """2 回目の起動（正常系）。"""
    # 準備
    root = repo_factory(_REPO_FILES)
    monkeypatch.chdir(root)
    main([])
    capsys.readouterr()
    before = {p.name: p.read_bytes() for p in (root / "docs/template/markdown").iterdir()}
    # 実行
    code = main([])
    # 検証
    assert code == 0
    assert capsys.readouterr().out == ""
    assert {p.name: p.read_bytes() for p in (root / "docs/template/markdown").iterdir()} == before


@pytest.mark.usefixtures("fake_build_outputs")
def test_main_when_build_error(
    repo_factory: RepoFactory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """対応する YAML のテンプレートが無い（異常系）。"""
    # 準備
    files = {k: v for k, v in _REPO_FILES.items() if k != "docs/template/template-config.yaml"}
    root = repo_factory(files)
    monkeypatch.chdir(root)
    # 実行
    code = main([])
    # 検証
    assert code == 2
    err = capsys.readouterr().err
    assert "template-config" in err
    assert "schemas/design/config.schema.yaml" in err
    assert sorted(p.name for p in (root / "docs/template/markdown").iterdir()) == ["config.md"]


@pytest.mark.usefixtures("fake_build_outputs")
def test_main_when_unexpected_error(
    repo_factory: RepoFactory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """想定していない例外（異常系）。"""

    # 準備
    def _broken(root: Path, outputs: object) -> object:
        del root, outputs
        msg = "壊れた"
        raise RuntimeError(msg)

    root = repo_factory(_REPO_FILES)
    monkeypatch.chdir(root)
    monkeypatch.setattr(build_markdown_templates, "list_differences", _broken)
    # 実行
    code = main(["--check"])
    # 検証
    assert code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Traceback" in captured.err


def test_build_outputs(repo_factory: RepoFactory) -> None:
    """雛形・記載例・管理用の YAML を作る（正常系）。"""
    # 準備
    root = repo_factory(_REPO_FILES)
    schemas = load_schemas(root)
    # 実行
    outputs = build_outputs(root, schemas, convert=_fake_convert)
    # 検証
    assert [o.path for o in outputs] == [
        PurePosixPath("docs/template/markdown/config.md"),
        PurePosixPath("docs/template/markdown/er.example.md"),
        PurePosixPath("docs/template/markdown/er.md"),
        PurePosixPath("docs/template/markdown/files.yaml"),
    ]
    assert [o.schema_path for o in outputs] == [
        PurePosixPath("schemas/design/config.schema.yaml"),
        PurePosixPath("schemas/design/er.schema.yaml"),
        PurePosixPath("schemas/design/er.schema.yaml"),
        PurePosixPath("schemas/design"),
    ]
    assert outputs[0].content == _CONFIG_MD
    assert outputs[1].content == 'er:{"id": "ER-1", "tables": [{"name": "tasks"}]}\n'


def test_build_outputs_when_template_missing(repo_factory: RepoFactory) -> None:
    """対応する YAML のテンプレートが無い（異常系）。"""
    # 準備
    files = {k: v for k, v in _REPO_FILES.items() if k != "docs/template/template-config.yaml"}
    root = repo_factory(files)
    schemas = load_schemas(root)
    # 実行・検証
    with pytest.raises(BuildError, match=r"template-config.*schemas/design/config\.schema\.yaml"):
        build_outputs(root, schemas, convert=_fake_convert)


def test_build_outputs_when_convert_fails(repo_factory: RepoFactory) -> None:
    """変換に失敗する（異常系）。"""

    # 準備
    def _failing(
        kind: str,
        path: PurePosixPath,
        data: Mapping[str, object],
        schema: Mapping[str, object],
    ) -> str:
        del path, data, schema
        if kind == "config":
            msg = "変換できない"
            raise ValueError(msg)
        return "ok\n"

    root = repo_factory(_REPO_FILES)
    schemas = load_schemas(root)
    # 実行・検証
    with pytest.raises(BuildError, match="変換に失敗しました") as excinfo:
        build_outputs(root, schemas, convert=_failing)
    assert excinfo.value.path == "schemas/design/config.schema.yaml"


def test_build_placeholder(repo_factory: RepoFactory) -> None:
    """値の種類ごとのプレースホルダ（正常系）。"""
    # 準備
    root = repo_factory(_REPO_FILES)
    schemas = load_schemas(root)
    # 実行
    result = build_placeholder("er.schema.yaml", schemas)
    # 検証
    assert result == {
        "id": "{ID}",
        "lead": "{冒頭リード}",
        "kind": "db / json",
        "draft": "true / false",
        "aliases": ["{別名}"],
        "tables": [{"name": "{物理名}"}],
    }


def test_build_placeholder_when_recursive_ref(repo_factory: RepoFactory) -> None:
    """再帰する $ref（正常系）。"""
    # 準備
    recursive = (
        "$schema: https://json-schema.org/draft/2020-12/schema\n"
        "title: 設定\n"
        "x-kind: config\n"
        "type: object\n"
        "properties:\n"
        "  entries:\n"
        "    type: array\n"
        "    title: 項目\n"
        "    items:\n"
        "      $ref: '#/$defs/entry'\n"
        "$defs:\n"
        "  entry:\n"
        "    type: object\n"
        "    properties:\n"
        "      name:\n"
        "        type: string\n"
        "        title: 名前\n"
        "      children:\n"
        "        type: array\n"
        "        title: 子\n"
        "        items:\n"
        "          $ref: '#/$defs/entry'\n"
    )
    root = repo_factory({"schemas/design/config.schema.yaml": recursive})
    schemas = load_schemas(root)
    # 実行
    result = build_placeholder("config.schema.yaml", schemas)
    # 検証
    assert result == {"entries": [{"name": "{名前}"}]}


def test_render_markdown() -> None:
    """dev-docs-table の行を削除する（正常系）。"""
    # 準備
    schema = {
        "title": "設定",
        "x-kind": "config",
        "type": "object",
        "properties": {
            "rows": {
                "type": "array",
                "title": "行",
                "x-heading": "行",
                "x-shape": "table",
                "x-key": "key",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "title": "キー"},
                        "value": {"type": "string", "title": "値"},
                    },
                },
            }
        },
    }
    data = {"rows": [{"key": "alpha", "value": "first"}, {"key": "beta", "value": "second"}]}
    # 実行
    result = render_markdown(
        "config", PurePosixPath("docs/template/markdown/config.md"), data, schema
    )
    # 検証
    assert "<!-- dev-docs-table:" not in result
    assert "alpha" in result
    assert "second" in result
    assert "\n\n\n" not in result
    assert result.endswith("\n")
    assert not result.endswith("\n\n")


def test_render_files_index() -> None:
    """雛形と記載例の行（正常系）。"""
    # 準備
    meta = TemplateMeta(
        name="テンプレート: ER 図",
        description="ER 図の書式を定め、ER 図を記載するときに参照する。",
        tags=("topic:er図", "topic:テンプレート"),
    )
    rows = [
        (PurePosixPath("docs/template/markdown/er.example.md"), "example", meta),
        (PurePosixPath("docs/template/markdown/er.md"), "template", meta),
    ]
    # 実行
    result = render_files_index(rows)
    # 検証
    assert result.startswith(
        "# yaml-language-server: $schema=../../../schemas/knowledge-files.schema.yaml\n"
    )
    data = YAML(typ="safe").load(result)
    assert data == {
        "files": [
            {
                "path": "er.example.md",
                "name": "テンプレート（Markdown）の記載例: ER 図",
                "description": "ER 図の書式を定め、ER 図を記載するときに参照する。",
                "tags": ["topic:er図", "topic:テンプレート"],
            },
            {
                "path": "er.md",
                "name": "テンプレート（Markdown）: ER 図",
                "description": "ER 図の書式を定め、ER 図を記載するときに参照する。",
                "tags": ["topic:er図", "topic:テンプレート"],
            },
        ]
    }
    files_schema = YAML(typ="safe").load(
        (_REPO / "schemas/knowledge-files.schema.yaml").read_text(encoding="utf-8")
    )
    assert list(Draft202012Validator(files_schema).iter_errors(data)) == []


def test_list_differences(tmp_path: Path) -> None:
    """違うファイル・無いファイル・対象に無い Markdown（正常系）。"""
    # 準備
    folder = tmp_path / "docs/template/markdown"
    folder.mkdir(parents=True)
    (folder / "a.md").write_text("A\n", encoding="utf-8")
    (folder / "b.md").write_text("旧 B\n", encoding="utf-8")
    (folder / "old.md").write_text("旧\n", encoding="utf-8")
    schema = PurePosixPath("schemas/design/er.schema.yaml")
    outputs = [
        Output(PurePosixPath("docs/template/markdown/a.md"), "A\n", schema),
        Output(PurePosixPath("docs/template/markdown/b.md"), "B\n", schema),
        Output(PurePosixPath("docs/template/markdown/c.md"), "C\n", schema),
    ]
    # 実行
    changed, stale = list_differences(tmp_path, outputs)
    # 検証
    assert [o.path for o in changed] == [
        PurePosixPath("docs/template/markdown/b.md"),
        PurePosixPath("docs/template/markdown/c.md"),
    ]
    assert stale == [PurePosixPath("docs/template/markdown/old.md")]


def test_list_differences_when_files_index_differs(tmp_path: Path) -> None:
    """files.yaml の生成元（正常系）。"""
    # 準備
    folder = tmp_path / "docs/template/markdown"
    folder.mkdir(parents=True)
    (folder / "files.yaml").write_text("files: []\n", encoding="utf-8")
    outputs = [
        Output(
            PurePosixPath("docs/template/markdown/files.yaml"),
            "files:\n  - path: er.md\n  - path: module.md\n",
            PurePosixPath("schemas/design"),
        )
    ]
    # 実行
    changed, stale = list_differences(tmp_path, outputs)
    # 検証
    assert [o.schema_path for o in changed] == [PurePosixPath("schemas/design")]
    assert stale == []
