"""設計書のテンプレートの生成（scripts/build_templates.py）の結合テスト。"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from _common import load_safe

if TYPE_CHECKING:
    from pathlib import Path

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]

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

# トップの x-rules、キーの $ref・enum・x-rules・x-bad-examples・x-used-by・入れ子の配列、トップの examples を 1 件持つスキーマ
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
    "    x-used-by:\n"
    "      - 検査で、参照の解決先にする。\n"
    "      - 生成で、ページの名前にする。\n"
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
    "    x-used-by:\n"
    "      - 実装で、テーブルの定義にする。\n"
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

# 決まりも悪い例も持たないスキーマ
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

# 対応表に行が無いスキーマ
_INDEX = (
    "$schema: https://json-schema.org/draft/2020-12/schema\n"
    "title: 目次\n"
    "description: フォルダの目次。\n"
    "x-kind: index\n"
    "type: object\n"
)

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
    "      | 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | 使用先 | examples |\n"
    "      | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    "      | name | 名前 | string | - | - | - | - | - | - |\n"
    "\n"
    "      <!-- /table -->\n"
)


def _repo(root: Path) -> Path:
    """4 件のスキーマと、items の古い template-er.yaml・生成した状態の template-config.yaml を持つ一時フォルダを作る。"""
    files = {
        "schemas/design/common.schema.yaml": _COMMON,
        "schemas/design/er.schema.yaml": _ER,
        "schemas/design/config.schema.yaml": _CONFIG,
        "schemas/design/index.schema.yaml": _INDEX,
        "docs/template/template-er.yaml": _TEMPLATE_ER_STALE,
        "docs/template/template-config.yaml": _TEMPLATE_CONFIG,
    }
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def test_normal(run_script: RunScript, tmp_path: Path) -> None:
    """スキーマが変わったテンプレートだけ、items を組み立て直して書き出す（正常系）。"""
    # 準備
    root = _repo(tmp_path / "repo")
    config_before = (root / "docs/template/template-config.yaml").read_bytes()
    # 実行
    first = run_script("build_templates", root)
    er_after = (root / "docs/template/template-er.yaml").read_bytes()
    second = run_script("build_templates", root)
    # 検証
    assert first.exit_code == 0
    assert first.stdout == "docs/template/template-er.yaml\n"
    doc = cast("dict[str, list[dict[str, str]]]", load_safe(er_after.decode("utf-8")))
    assert [item["id"] for item in doc["items"]] == [
        "overview",
        "rules-01",
        "item-list-01",
        "key-rules-01",
        "example-sample-01",
    ]
    assert doc["items"][0]["body"] == "データストアの構造をまとめる。"
    assert doc["items"][1]["body"] == "- 1 ファイル = 分類 1 つにする。"
    assert doc["items"][2]["body"] == (
        "<!-- table: data -->\n"
        "\n"
        "| 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | 使用先 | examples |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| id | ID | string | 必須 | - | - | 変わらない ID。 | 検査で、参照の解決先にする。<br>生成で、ページの名前にする。 | - |\n"
        "| lead | 冒頭リード | string | - | - | minLength: `1` | 1 行の説明。 | - | - |\n"
        "| kind | 種別 | string | - | `db` / `json` | - | - | - | - |\n"
        "| tables | テーブル | array | - | - | - | - | 実装で、テーブルの定義にする。 | - |\n"
        "| tables[].name | 物理名 | string | 必須 | - | pattern: `^[a-z_]+$` | - | - | `tasks` |\n"
        "\n"
        "<!-- /table -->"
    )
    assert doc["items"][3]["body"] == (
        "<!-- table: data -->\n"
        "\n"
        "| 名前 | 決まり | 悪い例 | 理由 |\n"
        "| --- | --- | --- | --- |\n"
        "| id | 改名でも変えない。 | - | - |\n"
        "| lead | - | 仕様を書く。 | 仕様は各項目へ分ける |\n"
        "\n"
        "<!-- /table -->"
    )
    assert doc["items"][4]["body"] == "```yaml\nid: ER-1\ntables:\n- name: tasks\n```"
    assert er_after.decode("utf-8").startswith(
        "# yaml-language-server: $schema=../../schemas/template.schema.yaml\n"
        "id: template-er\n"
        "kind: template\n"
        'name: "テンプレート: ER図"\n'
        "tags:\n"
        "  - name: topic:er図\n"
        "    main: true\n"
        "rev: 4\n"
        "items:\n"
    )
    assert (root / "docs/template/template-config.yaml").read_bytes() == config_before
    assert second.exit_code == 0
    assert second.stdout == ""
    assert (root / "docs/template/template-er.yaml").read_bytes() == er_after


def test_normal_recursive_ref(run_script: RunScript, tmp_path: Path) -> None:
    """配列の要素が自分と同じ定義を $ref で指すスキーマからも、キーの表を組み立てて書き出す（正常系）。"""
    # 準備
    root = _repo(tmp_path / "repo")
    run_script("build_templates", root)
    (root / "schemas/design/config.schema.yaml").write_text(
        _CONFIG
        + "  entries:\n"
        + "    type: array\n"
        + "    title: エントリ\n"
        + "    items:\n"
        + "      $ref: '#/$defs/entry'\n"
        + "$defs:\n"
        + "  entry:\n"
        + "    type: object\n"
        + "    properties:\n"
        + "      name:\n"
        + "        type: string\n"
        + "        title: 名前\n"
        + "      children:\n"
        + "        type: array\n"
        + "        title: 配下\n"
        + "        items:\n"
        + "          $ref: '#/$defs/entry'\n",
        encoding="utf-8",
    )
    # 実行
    result = run_script("build_templates", root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout == "docs/template/template-config.yaml\n"
    doc = cast(
        "dict[str, list[dict[str, str]]]",
        load_safe((root / "docs/template/template-config.yaml").read_text(encoding="utf-8")),
    )
    assert doc["items"][1]["body"] == (
        "<!-- table: data -->\n"
        "\n"
        "| 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | 使用先 | examples |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| name | 名前 | string | - | - | - | - | - | - |\n"
        "| entries | エントリ | array | - | - | - | - | - | - |\n"
        "| entries[].name | 名前 | string | - | - | - | - | - | - |\n"
        "| entries[].children | 配下 | array | - | - | - | - | - | - |\n"
        "\n"
        "<!-- /table -->"
    )


def test_error_when_ref_unresolvable(run_script: RunScript, tmp_path: Path) -> None:
    """解決できない $ref があれば、どのテンプレートも書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo(tmp_path / "repo")
    (root / "schemas/design/config.schema.yaml").write_text(
        _CONFIG + "  lead:\n    $ref: common.schema.yaml#/$defs/無い型\n", encoding="utf-8"
    )
    er_before = (root / "docs/template/template-er.yaml").read_bytes()
    config_before = (root / "docs/template/template-config.yaml").read_bytes()
    # 実行
    result = run_script("build_templates", root)
    # 検証
    assert result.exit_code == 2
    assert "schemas/design/config.schema.yaml" in result.stderr
    assert "common.schema.yaml#/$defs/無い型" in result.stderr
    assert (root / "docs/template/template-er.yaml").read_bytes() == er_before
    assert (root / "docs/template/template-config.yaml").read_bytes() == config_before


def test_error_when_schema_unreadable(run_script: RunScript, tmp_path: Path) -> None:
    """YAML として読めないスキーマがあれば、どのテンプレートも書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo(tmp_path / "repo")
    (root / "schemas/design/config.schema.yaml").write_text(
        "title: '閉じていない\n", encoding="utf-8"
    )
    er_before = (root / "docs/template/template-er.yaml").read_bytes()
    config_before = (root / "docs/template/template-config.yaml").read_bytes()
    # 実行
    result = run_script("build_templates", root)
    # 検証
    assert result.exit_code == 2
    assert "schemas/design/config.schema.yaml" in result.stderr
    assert (root / "docs/template/template-er.yaml").read_bytes() == er_before
    assert (root / "docs/template/template-config.yaml").read_bytes() == config_before


def test_error_when_template_missing(run_script: RunScript, tmp_path: Path) -> None:
    """種類のスキーマに対応するテンプレートの文書が無ければ、どのテンプレートも書き換えずに終わる（異常系）。"""
    # 準備
    root = _repo(tmp_path / "repo")
    (root / "docs/template/template-config.yaml").unlink()
    er_before = (root / "docs/template/template-er.yaml").read_bytes()
    # 実行
    result = run_script("build_templates", root)
    # 検証
    assert result.exit_code == 2
    assert "template-config" in result.stderr
    assert "schemas/design/config.schema.yaml" in result.stderr
    assert (root / "docs/template/template-er.yaml").read_bytes() == er_before
