"""scripts/build_templates.py の単体テスト。"""

from typing import TYPE_CHECKING

import pytest

from _common import load_document
from build_templates import (
    BuildError,
    _format_cell,  # pyright: ignore[reportPrivateUsage]
    _iter_keys,  # pyright: ignore[reportPrivateUsage]
    _render_key_rules,  # pyright: ignore[reportPrivateUsage]
    _render_key_table,  # pyright: ignore[reportPrivateUsage]
    KeyRow,
    build_items,
    load_schemas,
    main,
    replace_items,
)

if TYPE_CHECKING:
    from pathlib import Path

    from conftest import RepoFactory

# $ref の解決先を持つ共通のスキーマ
_COMMON = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 共通\n"
    "$defs:\n"
    "  summary:\n"
    "    type: string\n"
    "    title: 概要\n"
    "    description: 1 行の説明。\n"
    "    minLength: 1\n"
)

# トップの x-rules・キーの $ref・enum・x-rules・x-bad-examples・入れ子の配列・トップの examples を持つ種類のスキーマ
_ER = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: ER 図\n"
    "description: データストアの構造をまとめる。\n"
    "x-rules:\n"
    "  - 1 ファイル = 分類 1 つにする。\n"
    "x-kind: er\n"
    "type: object\n"
    "required:\n"
    "  - id\n"
    "properties:\n"
    "  id:\n"
    "    type: string\n"
    "    title: ID\n"
    "    description: 変わらない ID。\n"
    "    x-rules:\n"
    "      - 改名でも変えない。\n"
    "  lead:\n"
    "    $ref: common.schema.yaml#/$defs/summary\n"
    "    title: 冒頭リード\n"
    "    x-bad-examples:\n"
    "      - value: 仕様を書く。\n"
    "        reason: 仕様は各項目へ分ける\n"
    "  kind:\n"
    "    type: string\n"
    "    title: 種別\n"
    "    enum:\n"
    "      - db\n"
    "      - json\n"
    "  tables:\n"
    "    type: array\n"
    "    title: テーブル\n"
    "    items:\n"
    "      type: object\n"
    "      required:\n"
    "        - name\n"
    "      properties:\n"
    "        name:\n"
    "          type: string\n"
    "          title: 物理名\n"
    "          pattern: ^[a-z_]+$\n"
    "          examples:\n"
    "            - tasks\n"
    "examples:\n"
    "  - id: ER-1\n"
    "    tables:\n"
    "      - name: tasks\n"
)

# 決まりも悪い例も持たない種類のスキーマ
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

# _ER から組み立てた items
_ER_ITEMS = [
    {"id": "overview", "name": "概要", "body": "データストアの構造をまとめる。"},
    {"id": "rules-01", "name": "決まり", "body": "- 1 ファイル = 分類 1 つにする。"},
    {
        "id": "item-list-01",
        "name": "項目",
        "body": (
            "<!-- table: data -->\n"
            "\n"
            "| 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | examples |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            "| id | ID | string | 必須 | - | - | 変わらない ID。 | - |\n"
            "| lead | 冒頭リード | string | - | - | minLength: 1 | 1 行の説明。 | - |\n"
            "| kind | 種別 | string | - | db / json | - | - | - |\n"
            "| tables | テーブル | array | - | - | - | - | - |\n"
            "| tables[].name | 物理名 | string | 必須 | - | pattern: ^[a-z_]+$ | - | tasks |\n"
            "\n"
            "<!-- /table -->"
        ),
    },
    {
        "id": "key-rules-01",
        "name": "キーごとの決まり",
        "body": (
            "<!-- table: data -->\n"
            "\n"
            "| 名前 | 決まり | 悪い例 | 理由 |\n"
            "| --- | --- | --- | --- |\n"
            "| id | 改名でも変えない。 | - | - |\n"
            "| lead | - | 仕様を書く。 | 仕様は各項目へ分ける |\n"
            "\n"
            "<!-- /table -->"
        ),
    },
    {
        "id": "example-sample-01",
        "name": "記載例",
        "body": "```yaml\nid: ER-1\ntables:\n- name: tasks\n```",
    },
]

# _CONFIG から組み立てた items
_CONFIG_ITEMS = [
    {"id": "overview", "name": "概要", "body": "設定値の一覧。"},
    {
        "id": "item-list-01",
        "name": "項目",
        "body": (
            "<!-- table: data -->\n"
            "\n"
            "| 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | examples |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            "| name | 名前 | string | - | - | - | - | - |\n"
            "\n"
            "<!-- /table -->"
        ),
    },
]

# items が古い template-er.yaml
_TEMPLATE_ER_STALE = (
    "# yaml-language-server: $schema=../../schemas/template.schema.yaml\n"
    "id: template-er\n"
    "kind: template\n"
    'name: "テンプレート: ER図"\n'
    "tags:\n"
    "  - name: topic:er図\n"
    "    main: true\n"
    "rev: 4\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: |-\n"
    "      古い概要。\n"
)

# _ER から生成した状態の template-er.yaml
_TEMPLATE_ER = (
    "# yaml-language-server: $schema=../../schemas/template.schema.yaml\n"
    "id: template-er\n"
    "kind: template\n"
    'name: "テンプレート: ER図"\n'
    "tags:\n"
    "  - name: topic:er図\n"
    "    main: true\n"
    "rev: 4\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: |-\n"
    "      データストアの構造をまとめる。\n"
    "  - id: rules-01\n"
    "    name: 決まり\n"
    "    body: |-\n"
    "      - 1 ファイル = 分類 1 つにする。\n"
    "  - id: item-list-01\n"
    "    name: 項目\n"
    "    body: |-\n"
    "      <!-- table: data -->\n"
    "\n"
    "      | 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | examples |\n"
    "      | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    "      | id | ID | string | 必須 | - | - | 変わらない ID。 | - |\n"
    "      | lead | 冒頭リード | string | - | - | minLength: 1 | 1 行の説明。 | - |\n"
    "      | kind | 種別 | string | - | db / json | - | - | - |\n"
    "      | tables | テーブル | array | - | - | - | - | - |\n"
    "      | tables[].name | 物理名 | string | 必須 | - | pattern: ^[a-z_]+$ | - | tasks |\n"
    "\n"
    "      <!-- /table -->\n"
    "  - id: key-rules-01\n"
    "    name: キーごとの決まり\n"
    "    body: |-\n"
    "      <!-- table: data -->\n"
    "\n"
    "      | 名前 | 決まり | 悪い例 | 理由 |\n"
    "      | --- | --- | --- | --- |\n"
    "      | id | 改名でも変えない。 | - | - |\n"
    "      | lead | - | 仕様を書く。 | 仕様は各項目へ分ける |\n"
    "\n"
    "      <!-- /table -->\n"
    "  - id: example-sample-01\n"
    "    name: 記載例\n"
    "    body: |-\n"
    "      ```yaml\n"
    "      id: ER-1\n"
    "      tables:\n"
    "      - name: tasks\n"
    "      ```\n"
)

# _CONFIG から生成した状態の template-config.yaml
_TEMPLATE_CONFIG = (
    "# yaml-language-server: $schema=../../schemas/template.schema.yaml\n"
    "id: template-config\n"
    "kind: template\n"
    'name: "テンプレート: 設定"\n'
    "rev: 2\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: |-\n"
    "      設定値の一覧。\n"
    "  - id: item-list-01\n"
    "    name: 項目\n"
    "    body: |-\n"
    "      <!-- table: data -->\n"
    "\n"
    "      | 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | examples |\n"
    "      | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    "      | name | 名前 | string | - | - | - | - | - |\n"
    "\n"
    "      <!-- /table -->\n"
)

# 生成の対象のスキーマ 4 件と、items の古い template-er.yaml・生成した状態の template-config.yaml
_REPO_FILES = {
    "schemas/design/common.schema.yaml": _COMMON,
    "schemas/design/er.schema.yaml": _ER,
    "schemas/design/config.schema.yaml": _CONFIG,
    "schemas/design/index.schema.yaml": _INDEX,
    "docs/template/template-er.yaml": _TEMPLATE_ER_STALE,
    "docs/template/template-config.yaml": _TEMPLATE_CONFIG,
}


def test_main(
    repo_factory: RepoFactory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """items が古いテンプレートだけ書き換える（正常系）。"""
    # 準備
    root = repo_factory(_REPO_FILES)
    monkeypatch.chdir(root)
    # 実行
    code = main([])
    # 検証
    assert code == 0
    assert capsys.readouterr().out == "docs/template/template-er.yaml\n"
    assert (root / "docs/template/template-er.yaml").read_text(encoding="utf-8") == _TEMPLATE_ER
    assert (root / "docs/template/template-config.yaml").read_text(
        encoding="utf-8"
    ) == _TEMPLATE_CONFIG


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
    # 実行
    code = main([])
    # 検証
    assert code == 0
    assert capsys.readouterr().out == ""
    assert (root / "docs/template/template-er.yaml").read_text(encoding="utf-8") == _TEMPLATE_ER
    assert (root / "docs/template/template-config.yaml").read_text(
        encoding="utf-8"
    ) == _TEMPLATE_CONFIG


def test_main_when_template_missing(
    repo_factory: RepoFactory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """対応するテンプレートが無い（正常系）。"""
    # 準備
    root = repo_factory(_REPO_FILES)
    (root / "docs/template/template-config.yaml").unlink()
    monkeypatch.chdir(root)
    # 実行
    code = main([])
    # 検証
    assert code == 2
    err = capsys.readouterr().err
    assert "template-config" in err
    assert "schemas/design/config.schema.yaml" in err
    assert (root / "docs/template/template-er.yaml").read_text(
        encoding="utf-8"
    ) == _TEMPLATE_ER_STALE


def test_main_when_schema_broken(
    repo_factory: RepoFactory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """スキーマが読めない（正常系）。"""
    # 準備
    root = repo_factory(
        {**_REPO_FILES, "schemas/design/config.schema.yaml": "title: '閉じていない\n"}
    )
    monkeypatch.chdir(root)
    # 実行
    code = main([])
    # 検証
    assert code == 2
    assert "schemas/design/config.schema.yaml" in capsys.readouterr().err
    assert (root / "docs/template/template-er.yaml").read_text(
        encoding="utf-8"
    ) == _TEMPLATE_ER_STALE


def test_load_schemas(repo_factory: RepoFactory) -> None:
    """全てのスキーマを読んで登録する（正常系）。"""
    # 準備
    root = repo_factory(
        {"schemas/design/common.schema.yaml": _COMMON, "schemas/design/er.schema.yaml": _ER}
    )
    # 実行
    result = load_schemas(root)
    # 検証
    assert list(result.docs) == ["common.schema.yaml", "er.schema.yaml"]
    resolved = result.registry.resolver(base_uri="er.schema.yaml").lookup(
        "common.schema.yaml#/$defs/summary"
    )
    assert resolved.contents == {
        "type": "string",
        "title": "概要",
        "description": "1 行の説明。",
        "minLength": 1,
    }


def test_load_schemas_when_ref_unresolvable(repo_factory: RepoFactory) -> None:
    """解決できない $ref（異常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/common.schema.yaml": _COMMON,
            "schemas/design/er.schema.yaml": _ER.replace("$defs/summary", "$defs/無い型"),
        }
    )
    # 実行・検証
    with pytest.raises(BuildError, match=r"common\.schema\.yaml#/\$defs/無い型") as raised:
        load_schemas(root)
    assert raised.value.path == "schemas/design/er.schema.yaml"


def test_load_schemas_when_ref_unchecked(repo_factory: RepoFactory) -> None:
    """$ref を確認しない（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/common.schema.yaml": _COMMON,
            "schemas/design/er.schema.yaml": _ER.replace("$defs/summary", "$defs/無い型"),
        }
    )
    # 実行
    result = load_schemas(root, check_refs=False)
    # 検証
    assert list(result.docs) == ["common.schema.yaml", "er.schema.yaml"]


def test_load_schemas_when_unreadable(repo_factory: RepoFactory) -> None:
    """読めないスキーマ（異常系）。"""
    # 準備
    root = repo_factory({"schemas/design/er.schema.yaml": "title: '閉じていない\n"})
    # 実行・検証
    with pytest.raises(BuildError, match="スキーマを読めません") as raised:
        load_schemas(root)
    assert raised.value.path == "schemas/design/er.schema.yaml"


def test_build_items(repo_factory: RepoFactory) -> None:
    """5 項目の並び（正常系）。"""
    # 準備
    root = repo_factory(
        {"schemas/design/common.schema.yaml": _COMMON, "schemas/design/er.schema.yaml": _ER}
    )
    schemas = load_schemas(root)
    # 実行
    result = build_items("er.schema.yaml", schemas)
    # 検証
    assert result == _ER_ITEMS


def test_build_items_when_no_rules(repo_factory: RepoFactory) -> None:
    """決まりも悪い例も持たない（正常系）。"""
    # 準備
    root = repo_factory({"schemas/design/config.schema.yaml": _CONFIG})
    schemas = load_schemas(root)
    # 実行
    result = build_items("config.schema.yaml", schemas)
    # 検証
    assert result == _CONFIG_ITEMS


def test_build_items_when_many_examples(repo_factory: RepoFactory) -> None:
    """記載例が 2 件（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/config.schema.yaml": (
                _CONFIG + "examples:\n  - name: a\n  - name: b\n"
            )
        }
    )
    schemas = load_schemas(root)
    # 実行
    result = build_items("config.schema.yaml", schemas)
    # 検証
    assert result[2:] == [
        {"id": "example-sample-01", "name": "記載例 1", "body": "```yaml\nname: a\n```"},
        {"id": "example-sample-02", "name": "記載例 2", "body": "```yaml\nname: b\n```"},
    ]


def test_build_items_when_ref_unresolvable(repo_factory: RepoFactory) -> None:
    """解決できない $ref（異常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/common.schema.yaml": _COMMON,
            "schemas/design/er.schema.yaml": _ER.replace("$defs/summary", "$defs/無い型"),
        }
    )
    schemas = load_schemas(root, check_refs=False)
    # 実行・検証
    with pytest.raises(BuildError, match=r"\$defs/無い型"):
        build_items("er.schema.yaml", schemas)


def test_iter_keys(repo_factory: RepoFactory) -> None:
    """入れ子と $ref（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/common.schema.yaml": _COMMON,
            "schemas/design/a.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "type: object\n"
                "properties:\n"
                "  a:\n"
                "    type: object\n"
                "    title: A\n"
                "    properties:\n"
                "      b:\n"
                "        $ref: common.schema.yaml#/$defs/summary\n"
                "        title: B\n"
                "  c:\n"
                "    type: array\n"
                "    title: C\n"
                "    items:\n"
                "      type: object\n"
                "      properties:\n"
                "        d:\n"
                "          type: string\n"
                "          title: D\n"
            ),
        }
    )
    schemas = load_schemas(root)
    resolver = schemas.registry.resolver(base_uri="a.schema.yaml")
    # 実行
    result = list(_iter_keys(schemas.docs["a.schema.yaml"], resolver))
    # 検証
    assert [row.name for row in result] == ["a", "a.b", "c", "c[].d"]
    assert result[1].schema["title"] == "B"
    assert result[1].schema["description"] == "1 行の説明。"


def test_render_key_table() -> None:
    """列と制約と型（正常系）。"""
    # 準備
    rows = [
        KeyRow(
            name="a",
            schema={
                "type": ["string", "null"],
                "title": "A",
                "minLength": 1,
                "pattern": "^x$",
                "enum": ["x", "y"],
                "examples": ["x", "y"],
            },
            required=True,
        ),
        KeyRow(
            name="b",
            schema={"title": "B", "anyOf": [{"type": "string"}, {"type": "integer"}]},
            required=False,
        ),
    ]
    # 実行
    result = _render_key_table(rows)
    # 検証
    assert result == (
        "<!-- table: data -->\n"
        "\n"
        "| 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | examples |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| a | A | string / null | 必須 | x / y | pattern: ^x$, minLength: 1 | - | x / y |\n"
        "| b | B | string / integer | - | - | - | - | - |\n"
        "\n"
        "<!-- /table -->"
    )


def test_render_key_rules() -> None:
    """悪い例が 2 件（正常系）。"""
    # 準備
    rows = [
        KeyRow(
            name="a",
            schema={
                "x-rules": ["1 つ目。", "2 つ目。"],
                "x-bad-examples": [
                    {"value": "悪い 1", "reason": "理由 1"},
                    {"value": {"k": 1}, "reason": "理由 2"},
                ],
            },
            required=False,
        ),
        KeyRow(name="b", schema={"title": "B"}, required=False),
    ]
    # 実行
    result = _render_key_rules(rows)
    # 検証
    assert result == (
        "<!-- table: data -->\n"
        "\n"
        "| 名前 | 決まり | 悪い例 | 理由 |\n"
        "| --- | --- | --- | --- |\n"
        "| a | 1 つ目。<br>2 つ目。 | 悪い 1 | 理由 1 |\n"
        "|  |  | `{k: 1}` | 理由 2 |\n"
        "\n"
        "<!-- /table -->"
    )


def test_render_key_rules_when_none() -> None:
    """決まりを持つキーが無い（正常系）。"""
    # 準備
    rows = [KeyRow(name="b", schema={"title": "B"}, required=False)]
    # 実行
    result = _render_key_rules(rows)
    # 検証
    assert result is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(None, "-", id="none"),
        pytest.param("a|b\nc", "a\\|b<br>c", id="string"),
        pytest.param({"k": 1}, "`{k: 1}`", id="mapping"),
        pytest.param(True, "`true`", id="bool"),
    ],
)
def test_format_cell(value: object, expected: str) -> None:
    """値の種類ごと（正常系）。"""
    # 実行
    result = _format_cell(value)
    # 検証
    assert result == expected


def test_replace_items(tmp_path: Path) -> None:
    """items だけが変わる（正常系）。"""
    # 準備
    path = tmp_path / "template-er.yaml"
    path.write_text(_TEMPLATE_ER_STALE, encoding="utf-8")
    doc = load_document(_TEMPLATE_ER_STALE)
    # 実行
    result = replace_items(path, doc, _ER_ITEMS)
    # 検証
    assert result is True
    assert path.read_text(encoding="utf-8") == _TEMPLATE_ER


def test_replace_items_when_same(tmp_path: Path) -> None:
    """違いが無い（正常系）。"""
    # 準備
    path = tmp_path / "template-er.yaml"
    path.write_text(_TEMPLATE_ER, encoding="utf-8")
    before = path.stat().st_mtime_ns
    doc = load_document(_TEMPLATE_ER)
    # 実行
    result = replace_items(path, doc, _ER_ITEMS)
    # 検証
    assert result is False
    assert path.stat().st_mtime_ns == before
    assert path.read_text(encoding="utf-8") == _TEMPLATE_ER
