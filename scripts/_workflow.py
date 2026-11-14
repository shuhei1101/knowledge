"""入口が trigger のインターフェース定義と、GitHub Actions の workflow のファイルの突き合わせ。

check_all.py が同じフォルダから import する。
"""

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError

from _common import as_list, as_mapping, key_line, line_of, load_safe
from _lint import extract_map_mermaid

# 突き合わせる workflow のファイルを配置するフォルダ
WORKFLOWS_DIR = PurePosixPath(".github/workflows")

# on のイベントの下で、値を entry.value が含むかを比べるキー
TRIGGER_FILTERS = ("branches", "branches-ignore", "tags", "paths", "paths-ignore", "types")

# workflow のファイルの拡張子
_WORKFLOW_SUFFIXES = (".yml", ".yaml")

# 入口の種類のうち、workflow の起動を表すもの
_TRIGGER_KIND = "trigger"

# 文中のコードスパン
_CODE_SPAN = re.compile(r"`([^`]+)`")

# if の式を囲む ${{ }}
_EXPRESSION = re.compile(r"^\$\{\{\s*(?P<body>.*?)\s*\}\}$", re.DOTALL)

# flowchart の線: -- {ラベル} --> / -->|{ラベル}| / -.-> / ==> / --> / ---
_EDGE = re.compile(
    r"\s*(?:--\s+(?P<text>[^>]+?)\s+-->|-->\|(?P<pipe>[^|]*)\||-\.->|==>|-->|---)\s*"
)

# ノードの ID と、続く形状の括弧
_NODE = re.compile(r"^(?P<id>[A-Za-z0-9_]+)\s*(?P<shape>.*)$")

# subgraph の開き
_SUBGRAPH = re.compile(r"^subgraph\s+(?P<id>[A-Za-z0-9_]+)")

# 図の要素を持たない行の頭
_IGNORED_PREFIXES = ("%%", "classDef ", "class ", "style ", "linkStyle ", "click ", "direction ")

# 括弧の開きと閉じ
_OPENERS = "[({"
_CLOSERS = "])}"

# 括弧の中を表す文字
_MASK = "\0"

# 突き合わせの結果: （行、項目のパス、workflow の側の値）
type Mismatch = tuple[int, str, str]


@dataclass(frozen=True, slots=True)
class Flowchart:
    """map の Mermaid の flowchart 1 つから取り出したノード・subgraph・線。"""

    # ノードの ID → ラベル。開始・終わり（([...])）のノードを除く
    nodes: dict[str, str]
    # subgraph の ID → その中で定義したノードの ID
    subgraphs: dict[str, frozenset[str]]
    # （線の元の ID、線の先の ID、ラベル）。ラベルが無ければ空文字列
    edges: tuple[tuple[str, str, str], ...]


def check_workflows(
    root: Path, docs: Sequence[tuple[PurePosixPath, CommentedMap]]
) -> list[tuple[str, int, str, str]]:
    """入口が trigger のインターフェース定義ごとに workflow のファイルと突き合わせ、食い違いを違反として返却する。"""
    results: list[tuple[str, int, str, str]] = []
    checks: tuple[Callable[[CommentedMap, Mapping[str, object]], list[Mismatch]], ...] = (
        check_trigger,
        check_request,
        check_exclusivity,
        check_steps,
    )
    for path, doc in docs:
        entry = as_mapping(doc.get("entry"))
        # 入口が trigger でない設計書は突き合わせない
        if entry is None or entry.get("kind") != _TRIGGER_KIND:
            continue
        workflow_file = workflow_path(str(entry.get("value", "")))
        # entry.value が workflow のファイルを指さない設計書は突き合わせない
        if workflow_file is None:
            continue
        workflow = _load_workflow(root / workflow_file)
        if workflow is None:
            results.append(
                (
                    str(path),
                    line_of(doc, ("entry", "value")),
                    "entry.value",
                    f"workflow のファイル {workflow_file} を読み込めません",
                )
            )
            continue
        for check in checks:
            results.extend(
                (str(path), line, item, f"workflow のファイル {workflow_file} と食い違います: {value}")
                for line, item, value in check(doc, workflow)
            )
    return sorted(results, key=lambda result: (result[0], result[1]))


def _load_workflow(path: Path) -> Mapping[str, object] | None:
    """workflow のファイルを読み込む。無い・解釈できない・マッピングでなければ None。"""
    try:
        data = load_safe(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, YAMLError):
        return None
    return as_mapping(data)


def workflow_path(value: str) -> PurePosixPath | None:
    """entry.value の最初のコードスパンが workflow のファイルを指すとき、そのパスを返却する。"""
    match = _CODE_SPAN.search(value)
    if match is None:
        return None
    path = PurePosixPath(match[1])
    # WORKFLOWS_DIR の直下の YAML だけを workflow のファイルとして扱う
    if path.parent != WORKFLOWS_DIR or path.suffix not in _WORKFLOW_SUFFIXES:
        return None
    return path


def _text(value: object) -> str:
    """値を比べる文字列にする。真偽値は YAML の記法（true / false）にする。"""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _filter_values(event: object) -> list[str]:
    """イベントの下の起動を絞る条件の値を並べる。"""
    # schedule は cron を持つ要素の配列
    elements = as_list(event)
    if elements is not None:
        return [
            str(mapping["cron"])
            for element in elements
            if (mapping := as_mapping(element)) is not None and "cron" in mapping
        ]
    settings = as_mapping(event)
    if settings is None:
        return []
    values: list[str] = []
    for key in TRIGGER_FILTERS:
        raw = settings.get(key)
        # 1 つの値は文字列、複数の値は配列になる
        values.extend([str(raw)] if isinstance(raw, str) else [str(item) for item in as_list(raw) or []])
    return values


def check_trigger(doc: CommentedMap, workflow: Mapping[str, object]) -> list[Mismatch]:
    """on のイベント名と起動を絞る条件の値を、entry.value が含むかを比べる。"""
    entry = as_mapping(doc.get("entry")) or {}
    value = str(entry.get("value", ""))
    line = line_of(doc, ("entry", "value"))
    on = workflow.get("on")
    # on は文字列 1 つ・イベント名の配列・イベントごとの設定のマッピングのどれか
    events: list[tuple[str, object]]
    if isinstance(on, str):
        events = [(on, None)]
    elif (names := as_list(on)) is not None:
        events = [(str(name), None) for name in names]
    else:
        events = [(str(name), settings) for name, settings in (as_mapping(on) or {}).items()]
    expected: list[str] = []
    for name, settings in events:
        expected.append(name)
        expected.extend(_filter_values(settings))
    return [(line, "entry.value", item) for item in expected if item not in value]


def check_request(doc: CommentedMap, workflow: Mapping[str, object]) -> list[Mismatch]:
    """request を on.workflow_dispatch.inputs の名前の並び・型・必須・既定値と比べる。"""
    on = as_mapping(workflow.get("on")) or {}
    dispatch = as_mapping(on.get("workflow_dispatch")) or {}
    inputs = as_mapping(dispatch.get("inputs")) or {}
    requests = [as_mapping(item) or {} for item in as_list(doc.get("request")) or []]
    names = [str(request.get("name", "")) for request in requests]
    # 名前の並びが違えば、要素ごとには比べない
    if names != list(inputs):
        line = key_line(doc, "request") if "request" in doc else key_line(doc, "entry")
        return [(line, "request", ", ".join(inputs) or "inputs がありません")]
    results: list[Mismatch] = []
    for index, (name, request) in enumerate(zip(names, requests, strict=True)):
        settings = as_mapping(inputs[name]) or {}
        expected = {
            "type": _text(settings.get("type", "string")),
            "required": _text(settings.get("required", False)),
        }
        # 既定値は workflow が持つときだけ比べる
        if "default" in settings:
            expected["default"] = _text(settings["default"])
        for key, value in expected.items():
            if _text(request.get(key)) != value:
                line = line_of(doc, ("request", index, key))
                results.append((line, f"request[{name}].{key}", value))
    return results


def check_exclusivity(doc: CommentedMap, workflow: Mapping[str, object]) -> list[Mismatch]:
    """exclusivity が concurrency の group の値と cancel-in-progress: {値} を含むかを比べる。"""
    exclusivity = str(doc.get("exclusivity", ""))
    line = key_line(doc, "exclusivity") if "exclusivity" in doc else key_line(doc, "entry")
    concurrency = workflow.get("concurrency")
    # concurrency が無い workflow: cancel-in-progress を記載していれば食い違い
    if concurrency is None:
        if "cancel-in-progress" in exclusivity:
            return [(line, "exclusivity", "concurrency がありません")]
        return []
    # 文字列の concurrency は group だけを持つ
    settings = as_mapping(concurrency) or {}
    group = concurrency if isinstance(concurrency, str) else _text(settings.get("group", ""))
    cancel = _text(settings.get("cancel-in-progress", False))
    expected = [group, f"cancel-in-progress: {cancel}"]
    return [(line, "exclusivity", item) for item in expected if item not in exclusivity]


def _expression(value: object) -> str:
    """if の式から ${{ }} を除外した文字列を返却する。"""
    text = str(value).strip()
    match = _EXPRESSION.match(text)
    return match["body"] if match else text


def _flowchart_of(value: object) -> Flowchart | None:
    """項目の値の map から flowchart を読み取る。読み取れなければ None。"""
    if not isinstance(value, str):
        return None
    mermaid = extract_map_mermaid(value)
    return parse_flowchart(mermaid) if mermaid is not None else None


def check_steps(doc: CommentedMap, workflow: Mapping[str, object]) -> list[Mismatch]:
    """overall_flow・flows[].flow のノード・subgraph・線のラベルを、step の name・ジョブの ID・if と比べる。"""
    results: list[Mismatch] = []
    overall_line = key_line(doc, "overall_flow") if "overall_flow" in doc else key_line(doc, "entry")
    jobs = {str(job_id): as_mapping(job) or {} for job_id, job in (as_mapping(workflow.get("jobs")) or {}).items()}
    # ジョブごとの step の name と、if を持つ step（ジョブの ID、name、式）
    names_by_job: dict[str, list[str]] = {}
    step_ifs: list[tuple[str, str, str]] = []
    for job_id, job in jobs.items():
        names_by_job[job_id] = []
        for number, step in enumerate(as_list(job.get("steps")) or [], start=1):
            settings = as_mapping(step) or {}
            name = settings.get("name")
            # name の無い step は全体の流れに描けない
            if not isinstance(name, str) or not name:
                results.append(
                    (overall_line, "overall_flow", f"{job_id} の {number} 番目の step に name がありません")
                )
                continue
            names_by_job[job_id].append(name)
            if "if" in settings:
                step_ifs.append((job_id, name, _expression(settings["if"])))
    all_names = {name for names in names_by_job.values() for name in names}

    chart = _flowchart_of(doc.get("overall_flow"))
    # 全体の流れを読み取れなければ、step と分岐は比べない
    if chart is None:
        results.append((key_line(doc, "entry"), "overall_flow", "全体の流れがありません"))
    else:
        results.extend(_compare_overall(chart, overall_line, jobs, names_by_job, all_names, step_ifs))

    # flows[].flow の step は、全てのジョブの step の name のどれか
    for index, flow in enumerate(as_list(doc.get("flows")) or []):
        flow_chart = _flowchart_of((as_mapping(flow) or {}).get("flow"))
        if flow_chart is None:
            continue
        line = line_of(doc, ("flows", index, "flow"))
        unknown = [label for label in dict.fromkeys(flow_chart.nodes.values()) if label not in all_names]
        results.extend((line, f"flows[{index}].flow", label) for label in unknown)
    return results


def _compare_overall(
    chart: Flowchart,
    line: int,
    jobs: Mapping[str, Mapping[str, object]],
    names_by_job: Mapping[str, list[str]],
    all_names: set[str],
    step_ifs: Sequence[tuple[str, str, str]],
) -> list[Mismatch]:
    """全体の流れの flowchart を、ジョブ・step の name・if と比べる。"""
    results: list[Mismatch] = []
    labels = set(chart.nodes.values())
    # workflow にあって全体の流れに無い step と、全体の流れにあって workflow に無いノード
    results.extend((line, "overall_flow", name) for name in sorted(all_names - labels))
    results.extend((line, "overall_flow", label) for label in sorted(labels - all_names))
    # subgraph はジョブと 1 対 1
    results.extend(
        (line, "overall_flow", f"ジョブ {job_id} の subgraph がありません")
        for job_id in sorted(set(jobs) - set(chart.subgraphs))
    )
    results.extend(
        (line, "overall_flow", f"subgraph {graph_id} のジョブがありません")
        for graph_id in sorted(set(chart.subgraphs) - set(jobs))
    )
    # subgraph の中のノードは、そのジョブの step
    for graph_id, node_ids in sorted(chart.subgraphs.items()):
        if graph_id not in names_by_job:
            continue
        for node_id in sorted(node_ids):
            label = chart.nodes.get(node_id)
            if label is not None and label not in names_by_job[graph_id]:
                results.append((line, "overall_flow", f"{label} は {graph_id} の step ではありません"))
    # if を持つ step・ジョブは、そこへ入る線のラベルに式を持つ
    targets = [(name, expression, _node_ids(chart, job_id, name)) for job_id, name, expression in step_ifs]
    targets.extend(
        (job_id, _expression(job["if"]), set(chart.subgraphs.get(job_id, frozenset())))
        for job_id, job in jobs.items()
        if "if" in job
    )
    for name, expression, node_ids in targets:
        incoming = [label for _, target, label in chart.edges if target in node_ids]
        if not any(expression in label for label in incoming):
            results.append((line, "overall_flow", f"{name} の if（{expression}）が線のラベルにありません"))
    return results


def _node_ids(chart: Flowchart, job_id: str, name: str) -> set[str]:
    """ジョブの subgraph の中で、ラベルが step の name のノードの ID を返却する。"""
    members = chart.subgraphs.get(job_id, frozenset(chart.nodes))
    return {node_id for node_id in members if chart.nodes.get(node_id) == name}


def _mask(line: str) -> str:
    """括弧の中と |...| の中の文字を _MASK に置き換えた、同じ長さの文字列を返却する。"""
    masked: list[str] = []
    depth = 0
    in_pipe = False
    for char in line:
        # 括弧の外: | で線のラベルに出入りし、括弧の開きでノードの形状に入る
        if depth == 0:
            if char == "|":
                in_pipe = not in_pipe
                masked.append(char)
                continue
            if not in_pipe and char in _OPENERS:
                depth += 1
                masked.append(_MASK)
                continue
            masked.append(_MASK if in_pipe else char)
            continue
        # 括弧の中: 入れ子の深さだけを数える
        if char in _OPENERS:
            depth += 1
        elif char in _CLOSERS:
            depth -= 1
        masked.append(_MASK)
    return "".join(masked)


def _label(shape: str) -> str | None:
    """ノードの形状の括弧の中のラベルを返却する。括弧が無ければ None。"""
    for opener, closer in zip(_OPENERS, _CLOSERS, strict=True):
        if shape.startswith(opener) and shape.endswith(closer):
            return shape[1:-1].strip().strip('"')
    return None


def _parse_nodes(
    segment: str,
    masked: str,
    nodes: dict[str, str],
    terminals: set[str],
    members: set[str] | None,
) -> list[str]:
    """線で区切った 1 区間のノードを解釈し、ノードの ID の並びを返却する。"""
    ids: list[str] = []
    start = 0
    # & で並んだノードは 1 つずつに分ける（括弧の中の & は分けない）
    positions = [index for index, char in enumerate(masked) if char == "&"]
    for end in [*positions, len(segment)]:
        token = segment[start:end].strip()
        start = end + 1
        match = _NODE.match(token)
        if match is None:
            continue
        node_id, shape = match["id"], match["shape"].strip()
        ids.append(node_id)
        # 開始・終わり（([...])）のノードは step として扱わない
        if shape.startswith("([") and shape.endswith("])"):
            terminals.add(node_id)
            continue
        label = _label(shape)
        # ラベルを初めて持ったノードを、今いる subgraph に入れる
        if label is not None and node_id not in nodes and node_id not in terminals:
            nodes[node_id] = label
            if members is not None:
                members.add(node_id)
    return ids


def parse_flowchart(mermaid: str) -> Flowchart | None:
    """Mermaid の flowchart から、ノードの ID とラベル・subgraph・線を取り出す。"""
    lines = mermaid.strip().splitlines()
    if not lines or not lines[0].strip().startswith("flowchart"):
        return None
    nodes: dict[str, str] = {}
    terminals: set[str] = set()
    subgraphs: dict[str, set[str]] = {}
    stack: list[str] = []
    edges: list[tuple[str, str, str]] = []
    for raw in lines[1:]:
        line = raw.strip()
        if not line or line.startswith(_IGNORED_PREFIXES):
            continue
        # subgraph の開きと閉じ
        if (opening := _SUBGRAPH.match(line)) is not None:
            stack.append(opening["id"])
            subgraphs.setdefault(opening["id"], set())
            continue
        if line == "end":
            if stack:
                stack.pop()
            continue
        members = subgraphs[stack[-1]] if stack else None
        masked = _mask(line)
        # 線の位置は括弧と |...| の外だけで探す
        groups: list[list[str]] = []
        labels: list[str] = []
        start = 0
        for edge in _EDGE.finditer(masked):
            groups.append(_parse_nodes(line[start : edge.start()], masked[start : edge.start()], nodes, terminals, members))
            text = edge.group("text")
            pipe = edge.group("pipe")
            if text is not None:
                labels.append(line[edge.start("text") : edge.end("text")].strip().strip('"'))
            elif pipe is not None:
                labels.append(line[edge.start("pipe") : edge.end("pipe")].strip().strip('"'))
            else:
                labels.append("")
            start = edge.end()
        groups.append(_parse_nodes(line[start:], masked[start:], nodes, terminals, members))
        # 隣り合う区間のノードの組みごとに線を作る
        for left, right, label in zip(groups, groups[1:], labels, strict=False):
            edges.extend((source, target, label) for source in left for target in right)
    return Flowchart(
        nodes=nodes,
        subgraphs={graph_id: frozenset(ids) for graph_id, ids in subgraphs.items()},
        edges=tuple(edges),
    )
