"""scripts/_workflow.py の単体テスト。"""

import shutil
from pathlib import Path, PurePosixPath

from _common import load_document, load_safe
from _lint import extract_map_mermaid
from _workflow import (
    check_exclusivity,
    check_request,
    check_steps,
    check_trigger,
    check_workflows,
    parse_flowchart,
    workflow_path,
)

# リポジトリの直下
_ROOT = Path(__file__).resolve().parents[3]

# 公開文書の配信のワークフローのインターフェース定義と workflow のファイル
_INTERFACE = PurePosixPath("docs/interface/IF-137-2.yml.yaml")
_WORKFLOW = PurePosixPath(".github/workflows/pages.yml")


def _interface_text() -> str:
    """IF-137-2 の中身を返却する。"""
    return (_ROOT / _INTERFACE).read_text(encoding="utf-8")


def _workflow_text() -> str:
    """pages.yml の中身を返却する。"""
    return (_ROOT / _WORKFLOW).read_text(encoding="utf-8")


def _copy_repo(root: Path, workflow: str) -> None:
    """IF-137-2 のコピーと、指定した中身の pages.yml を root に配置する。"""
    (root / _INTERFACE).parent.mkdir(parents=True)
    shutil.copyfile(_ROOT / _INTERFACE, root / _INTERFACE)
    (root / _WORKFLOW).parent.mkdir(parents=True)
    (root / _WORKFLOW).write_text(workflow, encoding="utf-8")


def test_check_workflows(tmp_path: Path) -> None:
    """食い違いが無い（正常系）。"""
    # 準備
    _copy_repo(tmp_path, _workflow_text())
    docs = [(_INTERFACE, load_document(_interface_text()))]
    # 実行
    result = check_workflows(tmp_path, docs)
    # 検証
    assert result == []


def test_check_workflows_when_not_trigger(tmp_path: Path) -> None:
    """入口が trigger でない（正常系）。"""
    # 準備
    doc = load_document(
        'id: "IF-1"\ntitle: "検査"\nentry:\n  kind: operation\n'
        '  value: "`.github/workflows/pages.yml`"\n'
    )
    # 実行
    result = check_workflows(tmp_path, [(PurePosixPath("docs/interface/IF-1.py.yaml"), doc)])
    # 検証
    assert result == []


def test_check_workflows_when_file_missing(tmp_path: Path) -> None:
    """workflow のファイルが無い（正常系）。"""
    # 準備
    doc = load_document(
        'id: "IF-1"\ntitle: "配信"\nentry:\n  kind: trigger\n'
        '  value: "`.github/workflows/none.yml`。push"\n'
    )
    # 実行
    result = check_workflows(tmp_path, [(PurePosixPath("docs/interface/IF-1.yml.yaml"), doc)])
    # 検証
    assert len(result) == 1
    assert result[0][0] == "docs/interface/IF-1.yml.yaml"
    assert result[0][2] == "entry.value"
    assert ".github/workflows/none.yml" in result[0][3]


def test_check_workflows_when_differ(tmp_path: Path) -> None:
    """複数の食い違い（正常系）。"""
    # 準備
    workflow = (
        _workflow_text()
        .replace("cancel-in-progress: false", "cancel-in-progress: true")
        .replace(
            "      - name: 成果物をアップロードする\n",
            "      - name: 成果物の大きさを確かめる\n        run: du -sh _site\n"
            "      - name: 成果物をアップロードする\n",
        )
    )
    _copy_repo(tmp_path, workflow)
    docs = [(_INTERFACE, load_document(_interface_text()))]
    # 実行
    result = check_workflows(tmp_path, docs)
    # 検証
    assert len(result) == 2
    assert result[0][2] == "exclusivity"
    assert "cancel-in-progress: true" in result[0][3]
    assert result[1][2] == "overall_flow"
    assert "成果物の大きさを確かめる" in result[1][3]


def test_workflow_path() -> None:
    """workflow のパスを取り出す（正常系）。"""
    # 準備
    value = "`.github/workflows/pages.yml`。`develop` への `push` と、手動の起動（`workflow_dispatch`）"
    # 実行
    result = workflow_path(value)
    # 検証
    assert result == PurePosixPath(".github/workflows/pages.yml")


def test_workflow_path_when_not_workflow() -> None:
    """workflow を指さない（正常系）。"""
    # 準備
    other = "`scripts/a.py` を呼ぶ"
    plain = "リポジトリの直下で起動する"
    # 実行
    result = (workflow_path(other), workflow_path(plain))
    # 検証
    assert result == (None, None)


def test_check_trigger() -> None:
    """全て含む（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(_workflow_text())
    # 実行
    result = check_trigger(doc, workflow)
    # 検証
    assert result == []


def test_check_trigger_when_missing() -> None:
    """含まない値がある（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(
        _workflow_text().replace(
            "  workflow_dispatch:\n",
            "  workflow_dispatch:\n  pull_request:\n    paths:\n      - docs/**\n"
            "  schedule:\n    - cron: '0 0 * * *'\n",
        )
    )
    # 実行
    result = check_trigger(doc, workflow)
    # 検証
    assert [value for _, _, value in result] == ["pull_request", "docs/**", "schedule", "0 0 * * *"]
    assert {item for _, item, _ in result} == {"entry.value"}


def test_check_request() -> None:
    """一致する（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(_workflow_text())
    # 実行
    result = check_request(doc, workflow)
    # 検証
    assert result == []


def test_check_request_when_differ() -> None:
    """型と必須が違う（正常系）。"""
    # 準備
    doc = load_document(
        'id: "IF-1"\ntitle: "配信"\nentry:\n  kind: trigger\n'
        '  value: "`.github/workflows/a.yml`"\n'
        "request:\n  - name: target\n    type: string\n    required: false\n"
    )
    workflow = load_safe(
        "on:\n  workflow_dispatch:\n    inputs:\n      target:\n        type: boolean\n"
        "        required: true\n"
    )
    # 実行
    result = check_request(doc, workflow)
    # 検証
    assert [(item, value) for _, item, value in result] == [
        ("request[target].type", "boolean"),
        ("request[target].required", "true"),
    ]


def test_check_request_when_names_differ() -> None:
    """名前の並びが違う（正常系）。"""
    # 準備
    doc = load_document(
        'id: "IF-1"\ntitle: "配信"\nentry:\n  kind: trigger\n'
        '  value: "`.github/workflows/a.yml`"\n'
    )
    workflow = load_safe(
        "on:\n  workflow_dispatch:\n    inputs:\n      target:\n        type: string\n"
    )
    # 実行
    result = check_request(doc, workflow)
    # 検証
    assert len(result) == 1
    assert result[0][1] == "request"


def test_check_exclusivity() -> None:
    """含む（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(_workflow_text())
    # 実行
    result = check_exclusivity(doc, workflow)
    # 検証
    assert result == []


def test_check_exclusivity_when_differ() -> None:
    """cancel-in-progress が違う（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(
        _workflow_text().replace("cancel-in-progress: false", "cancel-in-progress: true")
    )
    # 実行
    result = check_exclusivity(doc, workflow)
    # 検証
    assert [(item, value) for _, item, value in result] == [
        ("exclusivity", "cancel-in-progress: true")
    ]


def test_check_exclusivity_when_no_concurrency() -> None:
    """concurrency が無い（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(
        _workflow_text().replace("concurrency:\n  group: pages\n  cancel-in-progress: false\n", "")
    )
    # 実行
    result = check_exclusivity(doc, workflow)
    # 検証
    assert [(item, value) for _, item, value in result] == [
        ("exclusivity", "concurrency がありません")
    ]


def test_check_steps() -> None:
    """一致する（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(_workflow_text())
    # 実行
    result = check_steps(doc, workflow)
    # 検証
    assert result == []


def test_check_steps_when_step_added() -> None:
    """overall_flow に無い step（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(
        _workflow_text().replace(
            "      - name: 成果物をアップロードする\n",
            "      - name: lint\n        run: echo lint\n      - name: 成果物をアップロードする\n",
        )
    )
    # 実行
    result = check_steps(doc, workflow)
    # 検証
    assert [(item, value) for _, item, value in result] == [("overall_flow", "lint")]


def test_check_steps_when_if_missing() -> None:
    """if が線のラベルに無い（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(
        _workflow_text().replace(
            "      - name: 成果物をアップロードする\n",
            "      - name: 成果物をアップロードする\n        if: ${{ success() }}\n",
        )
    )
    # 実行
    result = check_steps(doc, workflow)
    # 検証
    assert len(result) == 1
    assert result[0][1] == "overall_flow"
    assert "success()" in result[0][2]


def test_check_steps_when_unnamed() -> None:
    """name の無い step（正常系）。"""
    # 準備
    doc = load_document(_interface_text())
    workflow = load_safe(
        _workflow_text().replace(
            "      - name: Pages へ配信する\n",
            "      - uses: actions/checkout@v4\n      - name: Pages へ配信する\n",
        )
    )
    # 実行
    result = check_steps(doc, workflow)
    # 検証
    assert len(result) == 1
    assert result[0][1] == "overall_flow"
    assert "deploy の 1 番目" in result[0][2]


def test_check_steps_when_flow_label_unknown() -> None:
    """flows のラベルが step に無い（正常系）。"""
    # 準備
    text = _interface_text().replace(
        "a[ブランチを取得する] --> b[Node を入れる]", "a[別の step] --> b[Node を入れる]", 1
    )
    doc = load_document(text)
    workflow = load_safe(_workflow_text())
    # 実行
    result = check_steps(doc, workflow)
    # 検証
    assert [(item, value) for _, item, value in result] == [("flows[0].flow", "別の step")]


def test_parse_flowchart() -> None:
    """IF-137-2 の全体の流れを読み取る（正常系）。"""
    # 準備
    mermaid = extract_map_mermaid(str(load_document(_interface_text())["overall_flow"]))
    # 実行
    result = parse_flowchart(str(mermaid))
    # 検証
    assert result is not None
    assert set(result.nodes.values()) == {
        "ブランチを取得する",
        "Node を入れる",
        "uv を入れる",
        "Pages を設定する",
        "公開の文書を 1 枚の HTML にまとめる",
        "成果物に YAML が無いことを確かめる",
        "成果物をアップロードする",
        "Pages へ配信する",
    }
    assert result.subgraphs == {
        "build": frozenset({"a", "b", "c", "d", "e", "f", "g"}),
        "deploy": frozenset({"h"}),
    }
    assert ("g", "h", "成功（needs: build）") in result.edges
    assert {
        ("a", "ng", "失敗"),
        ("b", "ng", "失敗"),
        ("c", "ng", "失敗"),
        ("d", "ng", "失敗"),
        ("g", "ng", "失敗"),
    } <= set(result.edges)


def test_parse_flowchart_when_sequence() -> None:
    """flowchart でない（正常系）。"""
    # 準備
    mermaid = "sequenceDiagram\n  A->>B: hello"
    # 実行
    result = parse_flowchart(mermaid)
    # 検証
    assert result is None
