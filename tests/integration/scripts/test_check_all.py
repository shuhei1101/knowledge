"""全ての文書の検査（scripts/check_all.py）の結合テスト。"""

import shutil
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, cast

from ruamel.yaml import YAML

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]
type RepoFactory = Callable[[dict[str, str]], Path]

# リポジトリの直下
_REPO = Path(__file__).resolve().parents[3]
# description の文の数の上限
_MAX_SENTENCES = 2


def _descriptions(node: object) -> Iterator[str]:
    """スキーマの全ての深さの description の文字列を返す。値の例の中は辿らない。"""
    if isinstance(node, dict):
        for key, value in cast("dict[str, object]", node).items():
            if key == "description" and isinstance(value, str):
                yield value
            elif key not in {"examples", "x-bad-examples", "enum", "const", "default"}:
                yield from _descriptions(value)
    elif isinstance(node, list):
        for value in cast("list[object]", node):
            yield from _descriptions(value)


def test_normal(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """違反の無い文書だけなら終了コード 0 で終わる（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/a.yaml": "id: a\nkind: rule\nname: A\ndescription: A の文書\nitems:\n  - id: x\n    body: '[B](id:b)'\n",
            "docs/rule/b.yaml": "id: b\nkind: rule\nname: B\ndescription: B の文書\nitems:\n  - id: y\n    body: 本文。\n",
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout.splitlines()[-1] == "2 件の文書を検査し、違反は 0 件、警告は 0 件でした"


def test_normal_when_design_schemas_invalid(
    run_script: RunScript, repo_factory: RepoFactory
) -> None:
    """全ての設計書のスキーマを検査し終えてから、全ての誤りを違反として出して終了コード 1 で終わる（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "schemas/design/common.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 共通\n"
                "$defs:\n"
                "  id:\n"
                "    type: string\n"
                "    x-used-by:\n"
                "      - 実装で、ID にする。\n"
                "  plain:\n"
                "    type: string\n"
            ),
            # 3 行目の type が無い型の名前
            "schemas/design/bad-type.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\ntitle: 型\ntype: strin\n"
            ),
            # 5 行目の $ref が共通の型に無い $defs を指す
            "schemas/design/bad-ref.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 参照\n"
                "properties:\n"
                "  id:\n"
                "    $ref: common.schema.yaml#/$defs/missing\n"
            ),
            # 10 行目の examples[0] が required の id を持たない
            "schemas/design/bad-example.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: シナリオ\n"
                "type: object\n"
                "required:\n"
                "  - id\n"
                "properties:\n"
                "  id:\n"
                "    $ref: common.schema.yaml#/$defs/id\n"
                "examples:\n"
                "  - title: x\n"
            ),
            # 3 行目の x-rules が配列でない
            "schemas/design/bad-rules.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 決まり\n"
                "x-rules: 文字列\n"
            ),
            # 5 行目の a に x-used-by が無く、7 行目の b が x-used-by の無い型を指す。
            # x-used-by を持つ型を指す c と、if の条件の中の d は違反にしない
            "schemas/design/bad-used-by.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 使用先\n"
                "type: object\n"
                "properties:\n"
                "  a:\n"
                "    type: string\n"
                "  b:\n"
                "    $ref: common.schema.yaml#/$defs/plain\n"
                "  c:\n"
                "    $ref: common.schema.yaml#/$defs/id\n"
                "allOf:\n"
                "  - if:\n"
                "      properties:\n"
                "        d:\n"
                "          const: x\n"
                "    then:\n"
                "      required:\n"
                "        - a\n"
            ),
            # 2 行目の x-rules が配列でない
            "schemas/template.schema.yaml": "title: テンプレート\nx-rules: 文字列\n",
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    lines = result.stdout.splitlines()
    assert result.exit_code == 1
    assert len(lines) == 8
    assert lines[0].startswith("schemas/design/bad-example.schema.yaml:10: examples[0]: examples: ")
    assert lines[1].startswith(
        "schemas/design/bad-ref.schema.yaml:5: properties.id.$ref: "
        "$ref: common.schema.yaml#/$defs/missing "
    )
    assert lines[2].startswith("schemas/design/bad-rules.schema.yaml:3: x-rules: metaschema: ")
    assert lines[3].startswith("schemas/design/bad-type.schema.yaml:3: type: metaschema: ")
    assert lines[4] == (
        "schemas/design/bad-used-by.schema.yaml:5: properties.a: "
        "x-used-by: 使用先（x-used-by）が記載されていません"
    )
    assert lines[5] == (
        "schemas/design/bad-used-by.schema.yaml:7: properties.b: "
        "x-used-by: 使用先（x-used-by）が記載されていません"
    )
    assert lines[6].startswith("schemas/template.schema.yaml:2: x-rules: metaschema: ")
    assert lines[7] == "0 件の文書を検査し、違反は 7 件、警告は 0 件でした"


def test_normal_when_repository_schemas(run_script: RunScript, tmp_path: Path) -> None:
    """リポジトリの全てのスキーマと設計書のテンプレートが違反なしで通り、description が全て 2 文以内になっている（正常系）。"""
    # 準備
    root = tmp_path / "repo"
    root.mkdir()
    shutil.copytree(_REPO / "schemas", root / "schemas")
    shutil.copytree(_REPO / "docs" / "template", root / "docs" / "template")
    (root / "project-index.yaml").write_text("documents: []\n", encoding="utf-8")
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 0
    assert result.stdout.splitlines() == ["0 件の文書を検査し、違反は 0 件、警告は 0 件でした"]
    too_long = [
        (path.name, text)
        for path in sorted((_REPO / "schemas/design").glob("*.schema.yaml"))
        for text in _descriptions(YAML(typ="safe").load(path.read_text(encoding="utf-8")))
        if text.count("。") > _MAX_SENTENCES
    ]
    assert too_long == []


def test_normal_when_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """全ての文書を検査し終えてから、全ての違反を出して終了コード 1 で終わる（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/a.yaml": "id: a\nkind: rule\nname: A\nitems:\n  - id: x\n    body: 本文。\n",
            "docs/rule/b.yaml": "id: b\nkind: rule\nname: B\ndescription: B の文書\nitems:\n  - id: y\n    body: 本文。\n  - id: y\n    body: 本文。\n",
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    lines = result.stdout.splitlines()
    assert result.exit_code == 1
    assert lines[0].startswith("docs/rule/a.yaml:1: $: ")
    assert "description" in lines[0]
    assert lines[1].startswith("docs/rule/b.yaml:8: items[1].id: ")
    assert lines[-1] == "2 件の文書を検査し、違反は 2 件、警告は 0 件でした"


def test_normal_when_lint_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """失敗させるルールの lint の違反を、元の文書の YAML の行で出して終了コード 1 で終わる（正常系）。"""
    # 準備
    root = repo_factory(
        {
            # items[0].body の 3 行目（文書の 10 行目）が太字だけの段落
            "docs/rule/a.yaml": (
                "id: a\n"
                "kind: rule\n"
                "name: A\n"
                "description: A の文書\n"
                "items:\n"
                "  - id: x\n"
                "    body: |-\n"
                "      本文。\n"
                "\n"
                "      **太字だけの段落**\n"
            ),
            # 4 行目の引用符の無い値の # 以降がコメントになる
            "docs/rule/b.yaml": (
                "id: b\nkind: rule\nname: B\ndescription: B の文書 #bar\nitems:\n"
                "  - id: y\n    body: 本文。\n"
            ),
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    lines = result.stdout.splitlines()
    assert result.exit_code == 1
    assert any(
        line.startswith("docs/rule/a.yaml:10: items[0].body: markdownlint/MD036: ")
        for line in lines
    )
    assert any(line.startswith("docs/rule/b.yaml:4: -: yamllint/comments: ") for line in lines)


def test_normal_when_schemas_use_flow_style(
    run_script: RunScript, repo_factory: RepoFactory
) -> None:
    """schemas/ のスキーマのフロー形式を yamllint の違反にし、docs/ の文書のフロー形式は違反にしない（正常系）。"""
    # 準備
    rule_schema = (
        "$schema: https://json-schema.org/draft/2020-12/schema\n"
        "title: 規約\n"
        "allOf:\n"
        "  - $ref: knowledge-common.schema.yaml#/$defs/metadata\n"
        "properties:\n"
        "  kind:\n"
        "    const: rule\n"
        # 8 行目がフロー形式のシーケンス
        "required: [id, title]\n"
    )
    root = repo_factory(
        {
            "schemas/rule.schema.yaml": rule_schema,
            # 6 行目がフロー形式のシーケンスとマッピング
            "docs/rule/a.yaml": (
                "id: a\n"
                "kind: rule\n"
                "name: A\n"
                "title: A\n"
                "description: A の文書\n"
                "tags: [{name: scope:規約}]\n"
                "items:\n"
                "  - id: x\n"
                "    body: 本文。\n"
            ),
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    lines = result.stdout.splitlines()
    assert result.exit_code == 1
    assert any(
        line.startswith("schemas/rule.schema.yaml:8: -: yamllint/brackets: ") for line in lines
    )
    assert not any(line.startswith("docs/rule/a.yaml:") for line in lines)


def test_normal_when_only_warnings(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """警告にしたルールの違反は警告の行として出し、終了コードには数えない（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/a.yaml": (
                "id: a\nkind: rule\nname: A\ndescription: A の文書\nitems:\n"
                "  - id: x\n    body: A です。B です。\n"
            ),
        }
    )
    # 既定の設定は警告にするルールを持たないため、one-sentence-per-line だけを警告にした lint のフォルダを作る
    lint_dir = tmp_path / "lint"
    lint_dir.mkdir()
    for name in (
        ".markdownlint-cli2.jsonc",
        "no-inline-strong.mjs",
        ".yamllint.yaml",
        ".yamllint-schemas.yaml",
    ):
        shutil.copy(_REPO / "scripts/lint" / name, lint_dir / name)
    (lint_dir / ".textlintrc.json").write_text(
        '{"rules": {"one-sentence-per-line": {"severity": "warning"}}}\n', encoding="utf-8"
    )
    (lint_dir / "node_modules").symlink_to(_REPO / "scripts/lint/node_modules")
    # 実行
    result = run_script("check_all", root, args=["--lint-dir", str(lint_dir)])
    # 検証
    lines = result.stdout.splitlines()
    assert result.exit_code == 0
    assert any(
        line.startswith(
            "docs/rule/a.yaml:7: items[0].body: warning: textlint/one-sentence-per-line: "
        )
        for line in lines
    )
    assert lines[-1] == "1 件の文書を検査し、違反は 0 件、警告は 1 件でした"


def test_normal_when_word_list_copy_stale(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """対応表のコピーが正本から作り直したものと違えば、違反として出す（正常系）。"""
    # 準備
    word_list = (
        "id: word-list-ai-slop\n"
        "kind: word-list\n"
        "name: 対応表\n"
        "description: 対応表の文書\n"
        "entries:\n"
        "  - id: naosu\n"
        "    ng: 直す\n"
        "    ok: [修正]\n"
        "  - id: tasu\n"
        "    ng: 足す\n"
        "    ok: [追加]\n"
    )
    # コピーは正本の 1 行を除いたもの
    stale = '{\n  "entries": [\n    {\n      "id": "naosu",\n      "ng": "直す",\n      "ok": [\n        "修正"\n      ]\n    }\n  ]\n}\n'
    root = repo_factory(
        {
            "docs/word-list/word-list-ai-slop.yaml": word_list,
            "plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json": stale,
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 1
    line = next(
        line
        for line in result.stdout.splitlines()
        if line.startswith("plugins/slop-check/hooks/post-tool-use/word-list-ai-slop.json")
    )
    assert "scripts/build_word_list.py" in line


def test_normal_when_templates_out_of_date(
    run_script: RunScript, repo_factory: RepoFactory
) -> None:
    """設計書のテンプレートの items がスキーマから組み立てたものと違えば、違反として出す（正常系）。"""
    # 準備
    common = (
        "$schema: https://json-schema.org/draft/2020-12/schema\n"
        "title: 共通\n"
        "$defs:\n"
        "  id:\n"
        "    type: string\n"
        "    description: 変わらない ID。\n"
    )
    # x-rules を 1 件追加したスキーマ。テンプレートは追加する前に生成したもの
    er = (
        "$schema: https://json-schema.org/draft/2020-12/schema\n"
        "title: ER 図\n"
        "description: データストアの構造をまとめる。\n"
        "x-kind: er\n"
        "type: object\n"
        "properties:\n"
        "  id:\n"
        "    $ref: common.schema.yaml#/$defs/id\n"
        "    title: ID\n"
        "    x-rules:\n"
        "      - 改名でも変えない。\n"
    )
    template = (
        "id: template-er\n"
        "kind: template\n"
        "items:\n"
        "  - id: overview\n"
        "    name: 概要\n"
        "    body: |-\n"
        "      データストアの構造をまとめる。\n"
        "  - id: item-list-01\n"
        "    name: 項目\n"
        "    body: |-\n"
        "      <!-- table: data -->\n"
        "\n"
        "      | 名前 | title | 型 | 必須 | 選択肢 | 制約 | description | 使用先 | examples |\n"
        "      | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "      | id | ID | string | - | - | - | 変わらない ID。 | - | - |\n"
        "\n"
        "      <!-- /table -->\n"
    )
    root = repo_factory(
        {
            "schemas/design/common.schema.yaml": common,
            "schemas/design/er.schema.yaml": er,
            "docs/template/template-er.yaml": template,
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 1
    line = next(
        line
        for line in result.stdout.splitlines()
        if line.startswith("docs/template/template-er.yaml:3: items: ")
    )
    assert "schemas/design/er.schema.yaml" in line
    assert "scripts/build_templates.py" in line


# map の中の Mermaid に `:` の無いメッセージの行を持つ文書（13 行目が誤りの行）
_MAP_INVALID = (
    "id: rule-a\n"
    "kind: rule\n"
    "name: 規約 A\n"
    "description: 説明\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: |-\n"
    "      <!-- map -->\n"
    "\n"
    "      ```mermaid\n"
    "      sequenceDiagram\n"
    "        A->>B hello\n"
    "      ```\n"
    "\n"
    "      <!-- /map -->\n"
)

# 1 つの項目に誤りの無い map と前の記法のマーカーの表を持つ文書
_MAP_WITH_LEGACY_TABLE = (
    "id: rule-b\n"
    "kind: rule\n"
    "name: 規約 B\n"
    "description: 説明\n"
    "items:\n"
    "  - id: overview\n"
    "    name: 概要\n"
    "    body: |-\n"
    "      <!-- map -->\n"
    "\n"
    "      ```mermaid\n"
    "      sequenceDiagram\n"
    "        A->>B: hello\n"
    "      ```\n"
    "\n"
    "      <!-- /map -->\n"
    "\n"
    "      <!-- table: data -->\n"
    "\n"
    "      | 列 | 値 |\n"
    "      | --- | --- |\n"
    "      | a | 1 |\n"
    "\n"
    "      <!-- /table -->\n"
)

# インターフェース定義の行を加えた project-index.yaml
_CONFIG_WITH_INTERFACE = (
    'version: "3"\n'
    "name: knowledge\n"
    "documents:\n"
    "  - id: interface\n"
    "    paths:\n"
    "      - docs/interface/*.yaml\n"
    "    schema: schemas/design/interface.schema.yaml\n"
)

# スキルの設計書と、その工程を変更する前に生成した SKILL.md
_SKILL_DOC = (
    "id: a\n"
    "type: skill\n"
    "title: A を処理する\n"
    "summary: A を処理するスキル\n"
    "skill:\n"
    "  path: skills/a/SKILL.md\n"
    "steps:\n"
    "  - name: 取得する\n"
    "    body: A を一覧で取得する。\n"
)
_STALE_SKILL_MD = (
    "---\n"
    "name: a\n"
    "description: A を処理するスキル\n"
    "---\n"
    "\n"
    "<!-- docs/skill/a.yaml から生成した。このファイルを修正せず、設計書を修正して再生成する -->\n"
    "\n"
    "# A を処理する\n"
    "\n"
    "## 手順\n"
    "\n"
    "### 取得する\n"
    "\n"
    "A を取得する。\n"
)


def _copy_schemas(root: Path, names: list[str]) -> None:
    """リポジトリの schemas/design/ から、指定したスキーマを root にコピーする。"""
    (root / "schemas" / "design").mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copyfile(_REPO / "schemas" / "design" / name, root / "schemas" / "design" / name)


def test_normal_when_maps_invalid(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """map の誤りだけを違反として出し、前の記法のマーカーの legacy_mark は違反にしない（正常系）。"""
    # 準備
    root = repo_factory(
        {"docs/rule/rule-a.yaml": _MAP_INVALID, "docs/rule/rule-b.yaml": _MAP_WITH_LEGACY_TABLE}
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 1
    assert any(
        line.startswith("docs/rule/rule-a.yaml:13: items[0].body: mdmark/map_invalid: ")
        for line in result.stdout.splitlines()
    )
    assert "legacy_mark" not in result.stdout


def test_normal_when_workflows_differ_from_interfaces(
    run_script: RunScript, repo_factory: RepoFactory
) -> None:
    """入口が trigger のインターフェース定義と workflow のファイルの食い違いを、食い違い 1 件ごとに違反として出す（正常系）。"""
    # 準備
    workflow = (
        (_REPO / ".github/workflows/pages.yml")
        .read_text(encoding="utf-8")
        .replace("cancel-in-progress: false", "cancel-in-progress: true")
        .replace(
            "      - name: 成果物をアップロードする\n",
            "      - name: 成果物の大きさを確かめる\n        run: du -sh _site\n"
            "      - name: 成果物をアップロードする\n",
        )
    )
    root = repo_factory(
        {
            "project-index.yaml": _CONFIG_WITH_INTERFACE,
            "docs/interface/IF-137-2.yml.yaml": (
                _REPO / "docs/interface/IF-137-2.yml.yaml"
            ).read_text(encoding="utf-8"),
            ".github/workflows/pages.yml": workflow,
        }
    )
    _copy_schemas(root, ["interface.schema.yaml", "common.schema.yaml"])
    # 実行
    result = run_script("check_all", root)
    # 検証
    lines = [
        line
        for line in result.stdout.splitlines()
        if line.startswith("docs/interface/IF-137-2.yml.yaml:")
    ]
    assert result.exit_code == 1
    assert any(": exclusivity: " in line and "cancel-in-progress: true" in line for line in lines)
    assert any(": overall_flow: " in line and "成果物の大きさを確かめる" in line for line in lines)
    assert all(".github/workflows/pages.yml" in line for line in lines)


def test_normal_when_skills_out_of_date(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """スキルの設計書から組み立てた中身が SKILL.md と違えば、違反として出す（正常系）。"""
    # 準備
    root = repo_factory({"docs/skill/a.yaml": _SKILL_DOC, "skills/a/SKILL.md": _STALE_SKILL_MD})
    _copy_schemas(root, ["agent_flow.schema.yaml", "common.schema.yaml"])
    # 実行
    result = run_script("check_all", root)
    # 検証
    line = next(
        line for line in result.stdout.splitlines() if line.startswith("skills/a/SKILL.md:")
    )
    assert result.exit_code == 1
    assert "docs/skill/a.yaml" in line
    assert "uv run --frozen --script scripts/build_skills.py" in line


def test_error_when_mdmark_check_fails(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """mdmark の点検が失敗したら、他の検査の違反を出し終えてから終了コード 2 で終わる（異常系）。"""
    # 準備
    root = repo_factory(
        {
            "docs/rule/rule-a.yaml": _MAP_WITH_LEGACY_TABLE.replace("rule-b", "rule-a"),
            "docs/rule/rule-c.yaml": (
                "id: rule-c\nkind: rule\nname: 規約 C\nitems:\n  - id: x\n    name: 一つ目\n"
            ),
        }
    )
    # npx を、標準出力に何も出さずに終了コード 1 で終わるものに差し替える
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "npx").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    (bin_dir / "npx").chmod(0o755)
    # 実行
    result = run_script("check_all", root, path_prefix=bin_dir)
    # 検証
    assert result.exit_code == 2
    assert any(
        line.startswith("docs/rule/rule-c.yaml:") and ": schema: " in line
        for line in result.stdout.splitlines()
    )
    assert "mdmark の点検が失敗しました" in result.stderr
    assert "終了コード 1" in result.stderr


def test_error_when_check_cli_missing(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """markdownlint-cli2・textlint・npx のどれかが見つからなければ検査を始めずに終わる（異常系）。"""
    # 準備
    root = repo_factory({})
    missing = tmp_path / "missing-lint"
    # 実行
    result = run_script("check_all", root, args=["--lint-dir", str(missing)])
    # 検証
    assert result.exit_code == 2
    assert result.stderr.splitlines() == [
        "markdownlint-cli2 がありません。開発コマンドの『環境構築（クローン直後）』で入れてください",
        "textlint がありません。開発コマンドの『環境構築（クローン直後）』で入れてください",
    ]


def test_error_when_config_missing(run_script: RunScript, tmp_path: Path) -> None:
    """project-index.yaml が無いか読めなければ検査を始めずに終わる（異常系）。"""
    # 準備
    root = tmp_path / "empty"
    root.mkdir()
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 2
    assert "project-index.yaml" in result.stderr


def test_error_when_meta_schema_unusable(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """拡張したメタスキーマを使えなければ検査を始めずに終わる（異常系）。"""
    # 準備
    root = repo_factory({})
    (root / "schemas/meta.schema.yaml").unlink()
    # 実行
    result = run_script("check_all", root)
    # 検証
    assert result.exit_code == 2
    assert "schemas/meta.schema.yaml" in result.stderr


def test_normal_when_design_documents(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """行の schema が schemas/design/ のスキーマの設計書にも、スキーマの検査と lint を適用し、$ref は同じフォルダのスキーマで解く（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "project-index.yaml": (
                'version: "3"\n'
                "name: knowledge\n"
                "validators:\n"
                "  - id: knowledge-checks\n"
                "    run: [uv, run, --frozen, --script, scripts/knowledge_checks.py]\n"
                "    on: [write]\n"
                "documents:\n"
                "  - id: rule\n"
                "    paths:\n"
                "      - docs/rule/*.yaml\n"
                "    schema: schemas/rule.schema.yaml\n"
                "    validators:\n"
                "      - knowledge-checks\n"
                "  - id: scenario\n"
                "    paths:\n"
                "      - docs/scenario/*.yaml\n"
                "    schema: schemas/design/scenario.schema.yaml\n"
            ),
            # common.schema.yaml#/$defs/id を $ref で指す設計書のスキーマ
            "schemas/design/scenario.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: シナリオ\n"
                "type: object\n"
                "required:\n"
                "  - id\n"
                "  - title\n"
                "properties:\n"
                "  id:\n"
                "    $ref: common.schema.yaml#/$defs/id\n"
                "  title:\n"
                "    type: string\n"
                "    x-used-by:\n"
                "      - 生成で、見出しにする。\n"
            ),
            "schemas/design/common.schema.yaml": (
                "$schema: https://json-schema.org/draft/2020-12/schema\n"
                "title: 共通の型\n"
                "$defs:\n"
                "  id:\n"
                "    type: string\n"
                "    pattern: ^SC-\\d+-\\d+$\n"
                "    x-used-by:\n"
                "      - 実装で、ID にする。\n"
            ),
            "docs/rule/a.yaml": (
                "id: a\nkind: rule\nname: A\ndescription: A の文書\n"
                "items:\n  - id: x\n    body: '[B](id:b)'\n"
            ),
            "docs/rule/b.yaml": (
                "id: b\nkind: rule\nname: B\ndescription: B の文書\n"
                "items:\n  - id: y\n    body: 本文。\n"
            ),
            # 2 行目のコメントの前の空白が 1 つで、yamllint の comments の min-spaces-from-content だけに当たる
            "docs/scenario/SC-1-1.yaml": "id: SC-1-1\ntitle: シナリオ # bar\n",
        }
    )
    # 実行
    result = run_script("check_all", root)
    # 検証
    lines = result.stdout.splitlines()
    assert result.exit_code == 1
    assert [line for line in lines if line.startswith("docs/scenario/SC-1-1.yaml:")] == [
        "docs/scenario/SC-1-1.yaml:2: -: yamllint/comments: too few spaces before comment: expected 2"
    ]
    assert not any(line.startswith("schemas/") for line in lines)
