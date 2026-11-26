"""Markdown のテンプレートの生成（scripts/build_markdown_templates.py）の結合テスト。"""

import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from _common import load_safe

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]

# 入口のスクリプトの配置先
_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"

# 生成の出力のフォルダ（リポジトリの直下から）
_OUT = "docs/template/markdown"

# $ref の解決先を持つ共通のスキーマ
_COMMON = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 共通\n"
    "$defs:\n"
    "  summary:\n"
    "    type: string\n"
    "    title: 概要\n"
    "    description: 1 行の説明。\n"
)

# enum・真偽・title の無い文字列の配列（aliases）・入れ子の配列・x-shape: table・トップの examples を持つスキーマ
_ER = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: ER 図\n"
    "description: データストアの構造をまとめる。\n"
    "x-kind: er\n"
    "type: object\n"
    "required:\n"
    "  - id\n"
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
    "    x-heading: テーブル\n"
    "    x-shape: table\n"
    "    x-key: name\n"
    "    items:\n"
    "      type: object\n"
    "      properties:\n"
    "        name:\n"
    "          type: string\n"
    "          title: 物理名\n"
    "        columns:\n"
    "          type: array\n"
    "          title: 列\n"
    "          items:\n"
    "            type: string\n"
    "            title: 列名\n"
    "examples:\n"
    "  - id: ER-1\n"
    "    lead: タスクを保存する。\n"
    "    tables:\n"
    "      - name: tasks\n"
    "        columns:\n"
    "          - task_id\n"
    "  - id: ER-2\n"
)

# 記載例を 1 件持つ設定のスキーマ
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
    "examples:\n"
    "  - name: app\n"
)

# 対応表に行が無いスキーマ
_INDEX = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 目次\n"
    "description: フォルダの目次。\n"
    "x-kind: index\n"
    "type: object\n"
)

# 管理用の YAML へ description・tags をコピーする YAML のテンプレート（aliases はコピーしない）
_TEMPLATE_ER = (
    "id: template-er\n"
    "kind: template\n"
    'name: "テンプレート: ER図"\n'
    "description: ER 図の書式を定め、ER 図を作るときに参照する。\n"
    "aliases:\n"
    "  - ER図のテンプレート\n"
    "tags:\n"
    "  - name: topic:er図\n"
    "    main: true\n"
    "  - name: topic:テンプレート\n"
    "items: []\n"
)

_TEMPLATE_CONFIG = (
    "id: template-config\n"
    "kind: template\n"
    'name: "テンプレート: 設定"\n'
    "description: 設定の書式を定め、設定の設計書を作るときに参照する。\n"
    "tags:\n"
    "  - name: topic:設定\n"
    "items: []\n"
)

# config の変換で例外を送出し、それ以外は固定の Markdown を返却する dev-docs の差し替え
_FAKE_MARKDOWN = (
    "def schema_to_markdown(document, schema, context):\n"
    "    if document.kind == 'config':\n"
    "        raise RuntimeError('config の変換に失敗した')\n"
    "    return '# 差し替え\\n'\n"
)

# 受け取った値を属性に持つだけの dev-docs の型の差し替え
_FAKE_TYPE = (
    "class {name}:\n    def __init__(self, **kwargs):\n        self.__dict__.update(kwargs)\n"
)


def _write(root: Path, files: dict[str, str]) -> None:
    """リポジトリの直下からのパスと中身の組をファイルに書き出す。"""
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _repo(root: Path, *, with_er: bool = True) -> Path:
    """共通・設定・目次のスキーマと設定の YAML のテンプレート（with_er なら ER 図の分も）を持つ一時フォルダを作る。"""
    files = {
        "schemas/design/common.schema.yaml": _COMMON,
        "schemas/design/config.schema.yaml": _CONFIG,
        "schemas/design/index.schema.yaml": _INDEX,
        "docs/template/template-config.yaml": _TEMPLATE_CONFIG,
    }
    if with_er:
        files |= {
            "schemas/design/er.schema.yaml": _ER,
            "docs/template/template-er.yaml": _TEMPLATE_ER,
        }
    _write(root, files)
    return root


def _repo_without_er_outputs(run_script: RunScript, root: Path) -> Path:
    """config の雛形・記載例と files.yaml を生成した後に、ER 図のスキーマとテンプレートを加えた一時フォルダを作る。"""
    _repo(root, with_er=False)
    run_script("build_markdown_templates", root)
    _write(
        root,
        {
            "schemas/design/er.schema.yaml": _ER,
            "docs/template/template-er.yaml": _TEMPLATE_ER,
        },
    )
    return root


def _snapshot(root: Path) -> dict[str, bytes]:
    """docs/template/markdown/ の全てのファイルのバイト列を、ファイル名ごとに返却する。"""
    return {path.name: path.read_bytes() for path in sorted((root / _OUT).iterdir())}


def test_normal(run_script: RunScript, tmp_path: Path) -> None:
    """スキーマが変わった種類の雛形と記載例だけを書き出す（正常系）。"""
    # 準備
    root = _repo_without_er_outputs(run_script, tmp_path / "repo")
    config_before = (root / _OUT / "config.md").read_bytes()
    config_example_before = (root / _OUT / "config.example.md").read_bytes()
    # 実行
    first = run_script("build_markdown_templates", root)
    after = _snapshot(root)
    second = run_script("build_markdown_templates", root)
    # 検証
    assert first.exit_code == 0
    assert first.stdout == (
        "docs/template/markdown/er.example.md\n"
        "docs/template/markdown/er.md\n"
        "docs/template/markdown/files.yaml\n"
    )
    er = (root / _OUT / "er.md").read_text(encoding="utf-8")
    assert "db / json" in er
    assert "true / false" in er
    assert "{別名}" in er
    assert "{ID}" in er
    assert "{物理名}" in er
    assert "{列名}" in er
    assert "{id}" not in er
    assert "{draft}" not in er
    assert "{name}" not in er
    er_example = (root / _OUT / "er.example.md").read_text(encoding="utf-8")
    assert "ER-1" in er_example
    assert "task_id" in er_example
    assert "ER-2" not in er_example
    assert "<!-- dev-docs-table:" not in er
    assert "<!-- dev-docs-table:" not in er_example
    assert "<!-- table:" in er
    assert "<!-- table:" in er_example
    index = cast(
        "dict[str, list[dict[str, Any]]]",
        load_safe((root / _OUT / "files.yaml").read_text(encoding="utf-8")),
    )
    assert [row["path"] for row in index["files"]] == [
        "config.example.md",
        "config.md",
        "er.example.md",
        "er.md",
    ]
    assert index["files"][3] == {
        "path": "er.md",
        "name": "テンプレート（Markdown）: ER図",
        "description": "ER 図の書式を定め、ER 図を作るときに参照する。",
        "tags": ["topic:er図", "topic:テンプレート"],
    }
    assert index["files"][2]["name"] == "テンプレート（Markdown）の記載例: ER図"
    assert (root / _OUT / "config.md").read_bytes() == config_before
    assert (root / _OUT / "config.example.md").read_bytes() == config_example_before
    assert second.exit_code == 0
    assert second.stdout == ""
    assert _snapshot(root) == after


def test_normal_when_check_finds_differences(run_script: RunScript, tmp_path: Path) -> None:
    """--check では書き換えずに、ずれたファイルと生成元のスキーマを出す（正常系）。"""
    # 準備
    root = _repo_without_er_outputs(run_script, tmp_path / "repo")
    (root / _OUT / "old.md").write_text("# 旧\n", encoding="utf-8")
    before = _snapshot(root)
    # 実行
    result = run_script("build_markdown_templates", root, args=["--check"])
    # 検証
    assert result.exit_code == 1
    assert result.stdout == (
        "docs/template/markdown/er.example.md\tschemas/design/er.schema.yaml\n"
        "docs/template/markdown/er.md\tschemas/design/er.schema.yaml\n"
        "docs/template/markdown/files.yaml\tschemas/design\n"
        "docs/template/markdown/old.md\n"
    )
    assert _snapshot(root) == before


def test_normal_when_stale_markdown_exists(run_script: RunScript, tmp_path: Path) -> None:
    """対応する種類が無い Markdown を削除し、files.yaml からも行を除く（正常系）。"""
    # 準備
    root = _repo(tmp_path / "repo")
    run_script("build_markdown_templates", root)
    (root / _OUT / "old.md").write_text("# 旧\n", encoding="utf-8")
    index_path = root / _OUT / "files.yaml"
    index_path.write_text(
        index_path.read_text(encoding="utf-8")
        + "  - path: old.md\n    name: 旧\n    description: 旧。\n",
        encoding="utf-8",
    )
    # 実行
    result = run_script("build_markdown_templates", root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout == "docs/template/markdown/files.yaml\ndocs/template/markdown/old.md\n"
    assert not (root / _OUT / "old.md").exists()
    assert "old.md" not in index_path.read_text(encoding="utf-8")


def test_error_when_ref_unresolvable(run_script: RunScript, tmp_path: Path) -> None:
    """解決できない $ref があれば、どのファイルも書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo_without_er_outputs(run_script, tmp_path / "repo")
    (root / "schemas/design/config.schema.yaml").write_text(
        _CONFIG.replace(
            "examples:\n", "  lead:\n    $ref: common.schema.yaml#/$defs/無い型\nexamples:\n"
        ),
        encoding="utf-8",
    )
    before = _snapshot(root)
    # 実行
    result = run_script("build_markdown_templates", root)
    # 検証
    assert result.exit_code == 2
    assert "schemas/design/config.schema.yaml" in result.stderr
    assert "common.schema.yaml#/$defs/無い型" in result.stderr
    assert _snapshot(root) == before


def test_error_when_template_missing(run_script: RunScript, tmp_path: Path) -> None:
    """種類のスキーマに対応する YAML のテンプレートが無ければ、どのファイルも書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo_without_er_outputs(run_script, tmp_path / "repo")
    (root / "docs/template/template-config.yaml").unlink()
    before = _snapshot(root)
    # 実行
    result = run_script("build_markdown_templates", root)
    # 検証
    assert result.exit_code == 2
    assert "template-config" in result.stderr
    assert "schemas/design/config.schema.yaml" in result.stderr
    assert _snapshot(root) == before


def test_error_when_conversion_fails(run_script: RunScript, tmp_path: Path) -> None:
    """dev-docs の変換が例外を送出したら、どのファイルも書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo_without_er_outputs(run_script, tmp_path / "repo")
    before = _snapshot(root)
    # スクリプトのコピーの横に dev_docs を配置すると、取得した dev-docs より先に import される
    script_dir = tmp_path / "scripts"
    shutil.copytree(_SCRIPTS, script_dir, ignore=shutil.ignore_patterns("lint", "__pycache__"))
    _write(
        script_dir,
        {
            "dev_docs/__init__.py": "",
            "dev_docs/features/__init__.py": "",
            "dev_docs/features/convert/__init__.py": "",
            "dev_docs/features/convert/markdown.py": _FAKE_MARKDOWN,
            "dev_docs/features/convert/types.py": _FAKE_TYPE.format(name="RenderContext"),
            "dev_docs/integrations/__init__.py": "",
            "dev_docs/integrations/project_index/__init__.py": "",
            "dev_docs/integrations/project_index/types.py": _FAKE_TYPE.format(
                name="IndexedDocument"
            ),
        },
    )
    # 実行
    result = run_script("build_markdown_templates", root, script_dir=script_dir)
    # 検証
    assert result.exit_code == 2
    assert "schemas/design/config.schema.yaml" in result.stderr
    assert "config の変換に失敗した" in result.stderr
    assert _snapshot(root) == before
