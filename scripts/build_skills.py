# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "jsonschema>=4.26.0",
#     "ruamel.yaml==0.19.1",
# ]
# ///
"""docs/skill/ の type: skill の設計書から、skill.path の SKILL.md を組み立てて書き出す。

リポジトリの直下で起動する。スキルの設計書を変えたら実行し、SKILL.md を一緒に commit する。
全ての設計書を読み込んで検査し、全件の SKILL.md を組み立ててから、中身が違うものだけを書き出す。

Usage:
# SKILL.md を再生成する
uv run --frozen --script scripts/build_skills.py
"""

import argparse
import io
import json
import re
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

from build_templates import BuildError, load_schemas
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from _common import as_list, as_mapping, format_path, load_safe

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# リポジトリの直下からのスキルの設計書のフォルダ
SKILLS_DIR = PurePosixPath("docs/skill")

# schemas/design/ の中のエージェントフローのスキーマのファイル名
SCHEMA_NAME = "agent_flow.schema.yaml"

# frontmatter の後ろに配置する生成元のコメント
GENERATED_NOTE = (
    "<!-- {source} から生成した。このファイルを修正せず、設計書を修正して再生成する -->"
)

# 再生成するコマンド（docstring の Usage と同じ）
COMMAND = "uv run --frozen --script scripts/build_skills.py"

# 工程の埋め込みの ref（{設計書の id}#steps[{工程の name}]）
_STEP_REF = re.compile(r"^(?P<doc>[^#]+)#steps\[(?P<name>.+)\]$")

# 生成する設計書の type
_SKILL_TYPE = "skill"

# サブエージェントの種類が無いときに出す名前
_DEFAULT_AGENT_TYPE = "general-purpose"

# frontmatter の YAML を折り返さない幅
_NO_WRAP_WIDTH = 4096

# 終了コード。2 = 設計書かスキーマが読み込めないか合わずどのファイルも書き換えなかった、1 = 想定していない例外
_EXIT_NOT_BUILT = 2
_EXIT_UNEXPECTED = 1


@dataclass(frozen=True, slots=True)
class SkillPlan:
    """設計書 1 件から組み立てた SKILL.md の書き出す先と中身。"""

    # リポジトリの直下からの skill.path
    path: PurePosixPath
    # 組み立てた SKILL.md の中身（末尾は改行 1 つ）
    text: str


def _use_utf8(stream: object) -> None:
    """標準出力を UTF-8 にする（Windows の既定のエンコーディングで書き出さない）。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """全ての SKILL.md を組み立ててから、中身が違うものだけを書き出す。"""
    parser = argparse.ArgumentParser(
        description="docs/skill/ のスキルの設計書から、SKILL.md を書き出す"
    )
    parser.parse_args(argv)
    _use_utf8(sys.stdout)

    try:
        root = Path.cwd()
        # 書き出す前に全件を組み立てる。1 件でも失敗したら、どのファイルも書き換えない
        try:
            plans = plan_skills(root)
        except BuildError as error:
            print(str(error), file=sys.stderr)
            return _EXIT_NOT_BUILT
        written = sorted(plan.path for plan in plans if write_skill(root, plan))
        for path in written:
            print(path)
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返却する
        traceback.print_exc()
        return _EXIT_UNEXPECTED
    return 0


def plan_skills(root: Path) -> list[SkillPlan]:
    """全ての設計書を読み込んで検査し、type: skill の設計書ごとに書き出す SKILL.md を組み立てる。"""
    schemas = load_schemas(root)
    docs = load_skill_docs(root)

    # 全ての設計書をエージェントフローのスキーマで検査し、違反を全て集める
    validator = Draft202012Validator({"$ref": SCHEMA_NAME}, registry=schemas.registry)
    violations = [
        f"{path}: {format_path(list(error.absolute_path)) or '(最上位)'}: {error.message}"
        for path, doc in docs.items()
        for error in validator.iter_errors(cast("Any", doc))  # pyright: ignore[reportUnknownMemberType]
    ]
    if violations:
        raise BuildError(str(SKILLS_DIR), "設計書がスキーマに合いません\n" + "\n".join(violations))

    plans: list[SkillPlan] = []
    for path, doc in docs.items():
        # skill でない設計書（flow）は ref の参照先にだけ使用する
        if doc.get("type") != _SKILL_TYPE:
            continue
        text = render_skill(doc, path, resolve_steps(path, docs))
        skill_path = PurePosixPath(str(_mapping(doc.get("skill"))["path"]))
        # 解決したパスがリポジトリの外なら書き出さない
        if not (root / skill_path).resolve().is_relative_to(root.resolve()):
            raise BuildError(str(path), f"skill.path がリポジトリの外を指します: {skill_path}")
        plans.append(SkillPlan(path=skill_path, text=text))
    return plans


def load_skill_docs(root: Path) -> dict[PurePosixPath, Mapping[str, object]]:
    """docs/skill/*.yaml を読み込み、設計書のパスごとの中身を返却する。"""
    docs: dict[PurePosixPath, Mapping[str, object]] = {}
    for file in sorted((root / SKILLS_DIR).glob("*.yaml")):
        path = SKILLS_DIR / file.name
        try:
            data = load_safe(file.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, YAMLError) as error:
            raise BuildError(str(path), f"設計書を読み込めません: {error}") from error
        doc = as_mapping(data)
        if doc is None:
            raise BuildError(str(path), "設計書を読み込めません: 最上位がマッピングではありません")
        docs[path] = doc
    return docs


def resolve_steps(
    path: PurePosixPath, docs: Mapping[PurePosixPath, Mapping[str, object]]
) -> list[Mapping[str, object]]:
    """ref を持つ工程を、参照先の設計書の同じ名前の工程に置き換えた工程の並びを返却する。"""
    by_id = {str(doc.get("id")): doc for doc in docs.values()}
    resolved: list[Mapping[str, object]] = []
    for step in _list(docs[path].get("steps")):
        current = _mapping(step)
        # たどった ref。同じ ref へ戻ったら解決できない
        seen: list[str] = []
        while (ref := current.get("ref")) is not None:
            ref = str(ref)
            if ref in seen:
                raise BuildError(str(path), f"ref が同じ工程へ戻ります: {' → '.join([*seen, ref])}")
            seen.append(ref)
            current = _find_step(path, ref, by_id)
        resolved.append(current)
    return resolved


def _find_step(
    path: PurePosixPath, ref: str, by_id: Mapping[str, Mapping[str, object]]
) -> Mapping[str, object]:
    """ref が指す工程を返却する。参照先の設計書か工程が無ければ BuildError を送出する。"""
    matched = _STEP_REF.match(ref)
    target = by_id.get(matched["doc"]) if matched else None
    if matched is None or target is None:
        raise BuildError(str(path), f"ref の参照先の工程がありません: {ref}")
    for step in _list(target.get("steps")):
        candidate = _mapping(step)
        if candidate.get("name") == matched["name"]:
            return candidate
    raise BuildError(str(path), f"ref の参照先の工程がありません: {ref}")


def render_skill(
    doc: Mapping[str, object], source: PurePosixPath, steps: Sequence[Mapping[str, object]]
) -> str:
    """設計書と解決した工程から SKILL.md の中身を組み立てる。"""
    skill = _mapping(doc.get("skill"))
    sections = [
        render_frontmatter(doc),
        GENERATED_NOTE.format(source=source),
        f"# {doc.get('title') or _skill_name(skill)}",
    ]
    # 引数があれば、名前と説明の表を配置する
    arguments = [_mapping(argument) for argument in _list(skill.get("arguments"))]
    if arguments:
        rows = [
            f"| `${argument['name']}` | {_cell(argument['description'])} |"
            for argument in arguments
        ]
        sections.append("\n".join(["## 引数", "", "| 引数 | 説明 |", "| --- | --- |", *rows]))
    sections.append("## 手順")
    sections.extend(render_step(step) for step in steps)
    return "\n\n".join(sections) + "\n"


def render_frontmatter(doc: Mapping[str, object]) -> str:
    """設計書から SKILL.md の frontmatter を --- の行で囲んだ YAML にする。"""
    skill = _mapping(doc.get("skill"))
    arguments = [_mapping(argument) for argument in _list(skill.get("arguments"))]
    data: dict[str, object] = {
        "name": _skill_name(skill),
        "description": doc.get("summary"),
        "argument-hint": " ".join(str(argument["hint"]) for argument in arguments) or None,
        "arguments": [str(argument["name"]) for argument in arguments] or None,
        "allowed-tools": list(_list(skill.get("allowed_tools"))) or None,
    }
    # skill.frontmatter のキーを、その並びのまま続ける
    data.update(_mapping(skill.get("frontmatter")))
    present = {key: value for key, value in data.items() if value is not None}

    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.width = _NO_WRAP_WIDTH
    stream = io.StringIO()
    yaml.dump(present, stream)  # pyright: ignore[reportUnknownMemberType]
    return f"---\n{stream.getvalue()}---"


def render_step(step: Mapping[str, object]) -> str:
    """工程 1 つを ### のセクションにする。"""
    parts = [f"### {step['name']}"]
    # 条件があれば、その条件のときだけ行う旨を先に出す
    when = step.get("when")
    if when:
        parts.append(f"{when}だけ行う。")
    parts.append(str(step.get("body", "")).rstrip("\n"))
    # 呼ぶものがあれば、1 件 1 行の箇条書きにする
    calls = [_mapping(call) for call in _list(step.get("calls"))]
    if calls:
        parts.append("呼ぶもの:")
        parts.append("\n".join(render_call(call) for call in calls))
    return "\n\n".join(parts)


def render_call(call: Mapping[str, object]) -> str:
    """呼ぶもの 1 つを箇条書きの 1 行にする。"""
    kind = call.get("type")
    if kind == "tool":
        line = f"ツール `{call['tool']}`"
    elif kind == "mcp":
        line = f"MCP `{call['server']}` の `{call['tool']}`"
    elif kind == "command":
        line = f"コマンド `{call['command']}`"
    elif kind == "skill":
        line = f"スキル `{call['skill']}`"
    elif kind == "flow":
        line = f"エージェントフロー `{call['flow']}`"
    else:
        # agent: 種類が無ければ general-purpose、指示が無ければ実行するフロー
        agent_type = call.get("agent_type") or _DEFAULT_AGENT_TYPE
        line = f"サブエージェント `{agent_type}`: {call.get('instruction') or call.get('flow')}"
    # 引数があれば、1 行のインラインコードにして添える
    args = call.get("args")
    if args:
        line = f"{line} `{json.dumps(args, ensure_ascii=False)}`"
    return f"- {line}"


def write_skill(root: Path, plan: SkillPlan) -> bool:
    """中身が今のファイルと違うときだけ SKILL.md を書き出す。書き出したら True。"""
    path = root / plan.path
    data = plan.text.encode("utf-8")
    try:
        current = path.read_bytes()
    except FileNotFoundError:
        current = None
    if current == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    # 改行を LF のまま保つためバイト列で書き出す
    path.write_bytes(data)
    return True


def _skill_name(skill: Mapping[str, object]) -> str:
    """skill.name、無ければ skill.path の親のフォルダ名を返却する。"""
    name = skill.get("name")
    return str(name) if name else PurePosixPath(str(skill["path"])).parent.name


def _cell(value: object) -> str:
    """表のセルに入れる文字列にする（| をエスケープし、改行を空白にする）。"""
    return str(value).replace("|", "\\|").replace("\n", " ")


def _mapping(value: object) -> Mapping[str, object]:
    """マッピングならそのまま、そうでなければ空のマッピングを返却する。"""
    return as_mapping(value) or cast("Mapping[str, Any]", {})


def _list(value: object) -> list[object]:
    """配列ならそのまま、そうでなければ空の配列を返却する。"""
    return as_list(value) or []


if __name__ == "__main__":
    sys.exit(main())
