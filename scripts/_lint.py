"""全ての文書の検査で当てる markdownlint-cli2・textlint・yamllint と mdmark の map の点検の、在りかの確認と呼び出しと違反の行の対応。

check_all.py が同じフォルダから import する。
"""

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Literal, cast

from yamllint import linter  # pyright: ignore[reportMissingTypeStubs]
from yamllint.config import YamlLintConfig  # pyright: ignore[reportMissingTypeStubs]

from _common import MDMARK_TAG, DocumentError, format_path, iter_strings, load_document

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# lint のフォルダの node_modules/.bin/ から引くコマンド名
MARKDOWNLINT = "markdownlint-cli2"
TEXTLINT = "textlint"

# パスの末尾がこのキーの文字列を Markdown の項目として lint を当てる
MARKDOWN_KEY = "body"

# 設定と npm の依存を持つフォルダの既定
DEFAULT_LINT_DIR = Path(__file__).parent / "lint"

# lint のフォルダの中の設定ファイル
_MARKDOWNLINT_CONFIG = ".markdownlint-cli2.jsonc"
_TEXTLINT_CONFIG = ".textlintrc.json"
_YAMLLINT_CONFIG = ".yamllint.yaml"

# schemas/ のスキーマに当てる yamllint の設定。brackets・braces の forbid: non-empty だけを持つ
YAMLLINT_SCHEMAS_CONFIG = ".yamllint-schemas.yaml"

# ファイル全体に当てた lint の項目のパス
_WHOLE_FILE = "-"

# markdownlint-cli2 と textlint の終了コード。0 = error の違反なし、1 = error の違反あり。それ以外は CLI 自身の失敗
_EXIT_CODES = (0, 1)

# textlint の severity の warning
_TEXTLINT_WARNING = 1

# YAML として読めない誤りで yamllint の rule が None のときのルール名
_YAMLLINT_SYNTAX = "syntax"

# markdownlint-cli2 の標準エラーの違反の行: {ファイル}:{行}[:{列}] {error|warning} {ルール名}/{別名} {内容}
_MARKDOWNLINT_LINE = re.compile(
    r"^(?P<file>.+?\.md):(?P<line>\d+)(?::\d+)? (?P<level>error|warning) "
    r"(?P<rule>[^/\s]+)/\S+ (?P<message>.*)$"
)

# この文字列を含む文字列の項目を map の点検にかける
MAP_START = "<!-- map -->"

# map の範囲の閉じのマーカー
_MAP_END = "<!-- /map -->"

# map の点検でつないだ項目の間に挟む空行
_MAP_SEPARATOR = "\n\n\n"

# mdmark の check --text のずれの行: -:{行}: {種類}: {内容}
_MDMARK_LINE = re.compile(r"^-:(?P<line>\d+): (?P<kind>[a-z_]+): (?P<message>.*)$")

# mdmark の check --text が点検したときの最後の行: ずれ {件数} 件
_MDMARK_SUMMARY = re.compile(r"^ずれ \d+ 件$")

# 違反にする mdmark のずれの種類の接頭辞（map の誤り）
_MAP_KIND_PREFIX = "map_"

type LintTool = Literal["markdownlint", "textlint", "yamllint", "mdmark"]


@dataclass(frozen=True)
class LintSource:
    """一時の .md 1 つに書き出す、文書の Markdown の項目か .md の文書 1 つ。"""

    # 文書のリポジトリの直下からのパス
    path: PurePosixPath
    # 項目のパス。.md の文書は -
    item_path: str
    # 本文の 1 行目の文書の行（1 始まり）。.md の文書は 1
    start_line: int
    text: str


@dataclass(frozen=True)
class LintFinding:
    """3 つの CLI のどれかが返した違反 1 件を、元の文書の行にしたもの。"""

    path: PurePosixPath
    # 元の文書の行（1 始まり）
    line: int
    # 項目のパス。ファイル全体に当てた lint は -
    item_path: str
    tool: LintTool
    rule: str
    message: str
    # CLI が warning で返したか
    warning: bool


class MdmarkCheckError(Exception):
    """mdmark の check --text の終了コードが 0・1 でないか、標準出力の最後の行が ずれ {件数} 件 でない。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class LintOutputError(Exception):
    """markdownlint-cli2・textlint の終了コードが 0・1 でないか、出力が読めない。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def find_lint_clis(lint_dir: Path) -> dict[str, str | None]:
    """lint のフォルダの node_modules/.bin/ から markdownlint-cli2・textlint の実行ファイルを引く。"""
    bin_dir = lint_dir / "node_modules" / ".bin"
    return {name: shutil.which(name, path=bin_dir) for name in (MARKDOWNLINT, TEXTLINT)}


def collect_sources(path: PurePosixPath, text: str) -> list[LintSource]:
    """文書 1 件から、Markdown の項目か .md の文書の全体を取り出す。"""
    # .md の文書は全体を 1 つとして当てる
    if path.suffix == ".md":
        return [LintSource(path, _WHOLE_FILE, 1, text)]
    try:
        doc = load_document(text)
    except DocumentError:
        # 読めない文書の違反は文書 1 件の検査が出す
        return []
    return [
        LintSource(path, format_path(parts), line, value)
        for parts, line, value in iter_strings(doc)
        if parts and parts[-1] == MARKDOWN_KEY
    ]


def collect_map_sources(path: PurePosixPath, text: str) -> list[LintSource]:
    """YAML の文書 1 件から、値に map の開きのマーカーを含む文字列の項目を取り出す。"""
    # map の点検は YAML の文書の項目だけに当てる
    if path.suffix not in {".yaml", ".yml"}:
        return []
    try:
        doc = load_document(text)
    except DocumentError:
        # 読めない文書の違反は文書 1 件の検査が出す
        return []
    return [
        LintSource(path, format_path(parts), line, value)
        for parts, line, value in iter_strings(doc)
        if MAP_START in value
    ]


def extract_map_mermaid(text: str) -> str | None:
    """最初の map の範囲の中の、最初の mermaid のコードブロックの中身を返却する。"""
    start = text.find(MAP_START)
    if start < 0:
        return None
    end = text.find(_MAP_END, start)
    # 閉じのマーカーが無ければ map の範囲を決められない
    if end < 0:
        return None
    lines = text[start + len(MAP_START) : end].splitlines()
    try:
        opening = next(index for index, line in enumerate(lines) if line.strip() == "```mermaid")
    except StopIteration:
        return None
    body: list[str] = []
    for line in lines[opening + 1 :]:
        # 閉じのフェンスで mermaid のブロックが終わる
        if line.strip() == "```":
            return "\n".join(body)
        body.append(line)
    # 閉じのフェンスが無い
    return None


def run_map_check(sources: Sequence[LintSource], npx: str) -> list[LintFinding]:
    """map を含む全ての項目をつないで mdmark の check --text - を 1 回呼び、map のずれを元の文書の行で返却する。"""
    if not sources:
        return []
    # 項目ごとの、つないだ Markdown の中の開始行（1 始まり）を控えてつなぐ
    starts: list[int] = []
    line = 1
    for source in sources:
        starts.append(line)
        line += source.text.count("\n") + _MAP_SEPARATOR.count("\n")
    joined = _MAP_SEPARATOR.join(source.text for source in sources) + "\n"
    with tempfile.TemporaryDirectory() as workdir:
        # 一時のフォルダで呼び、リポジトリの設定ファイルを読ませない
        result = subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
            [npx, "-y", f"github:shuhei1101/mdmark#{MDMARK_TAG}", "check", "--text", "-"],
            cwd=workdir,
            input=joined,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    lines = [text for text in result.stdout.splitlines() if text.strip()]
    # 点検したときだけ、終了コードが 0・1 で最後の行が ずれ {件数} 件 になる
    if result.returncode not in _EXIT_CODES or not lines or not _MDMARK_SUMMARY.match(lines[-1]):
        message = f"mdmark が終了コード {result.returncode} で終わりました: {result.stderr.strip()}"
        raise MdmarkCheckError(message)
    findings: list[LintFinding] = []
    for text in lines[:-1]:
        match = _MDMARK_LINE.match(text)
        # map の誤りの種類だけを違反にし、legacy_mark など他の種類は捨てる
        if match is None or not match["kind"].startswith(_MAP_KIND_PREFIX):
            continue
        number = int(match["line"])
        # 行を含む項目は、開始行が mdmark の行以下の最後の項目
        index = max(i for i, start in enumerate(starts) if start <= number)
        findings.append(
            _finding(
                sources[index],
                number - starts[index] + 1,
                "mdmark",
                match["kind"],
                match["message"],
                warning=False,
            )
        )
    return findings


def _run_cli(name: str, args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """CLI を呼び、終了コードが 0・1 でなければ LintOutputError を送出する。"""
    result = subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
        list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    # 0・1 以外は CLI 自身の失敗: 標準エラーの最後の行を理由にする
    if result.returncode not in _EXIT_CODES:
        lines = result.stderr.strip().splitlines()
        last = lines[-1] if lines else ""
        message = f"{name} が終了コード {result.returncode} で終わりました: {last}"
        raise LintOutputError(message)
    return result


def _source_index(file_path: str) -> int:
    """一時の .md のファイル名（{添字:05d}.md）から sources の添字を返す。"""
    return int(Path(file_path).stem)


def _finding(
    source: LintSource, line: int, tool: LintTool, rule: str, message: str, *, warning: bool
) -> LintFinding:
    """一時の .md の行を元の文書の行にした違反を作る。"""
    return LintFinding(
        path=source.path,
        line=source.start_line + line - 1,
        item_path=source.item_path,
        tool=tool,
        rule=rule,
        # 複数行の内容（textlint の理由・修正の行など）は 1 行にまとめる
        message=" ".join(message.split("\n")),
        warning=warning,
    )


def _parse_markdownlint(stderr: str, sources: Sequence[LintSource]) -> list[LintFinding]:
    """markdownlint-cli2 の標準エラーの違反の行を、元の文書の行の違反にする。"""
    findings: list[LintFinding] = []
    for raw in stderr.splitlines():
        matched = _MARKDOWNLINT_LINE.match(raw)
        # 違反の行でない行（要約など）は読まない
        if matched is None:
            continue
        source = sources[_source_index(matched.group("file"))]
        findings.append(
            _finding(
                source,
                int(matched.group("line")),
                "markdownlint",
                matched.group("rule"),
                matched.group("message"),
                warning=matched.group("level") == "warning",
            )
        )
    return findings


def _parse_textlint(stdout: str, sources: Sequence[LintSource]) -> list[LintFinding]:
    """textlint の JSON の標準出力を、元の文書の行の違反にする。"""
    try:
        data: object = json.loads(stdout)
    except json.JSONDecodeError as error:
        message = f"{TEXTLINT} の出力を読めません"
        raise LintOutputError(message) from error
    if not isinstance(data, list):
        message = f"{TEXTLINT} の出力を読めません"
        raise LintOutputError(message)
    findings: list[LintFinding] = []
    for result in cast("list[dict[str, object]]", data):
        source = sources[_source_index(cast("str", result["filePath"]))]
        for message in cast("list[dict[str, object]]", result["messages"]):
            findings.append(
                _finding(
                    source,
                    cast("int", message["line"]),
                    "textlint",
                    cast("str", message["ruleId"]),
                    cast("str", message["message"]),
                    warning=message["severity"] == _TEXTLINT_WARNING,
                )
            )
    return findings


def run_markdown_lints(
    sources: Sequence[LintSource], lint_dir: Path, clis: Mapping[str, str]
) -> list[LintFinding]:
    """全ての Markdown を一時の .md に書き出し、markdownlint-cli2・textlint を 1 回ずつ呼んで、違反を元の文書の行で返す。"""
    if not sources:
        return []
    with tempfile.TemporaryDirectory() as folder:
        # sources の添字をファイル名にし、違反のファイル名から元の項目を引く
        files: list[str] = []
        for index, source in enumerate(sources):
            path = Path(folder) / f"{index:05d}.md"
            # 文書の項目の |- は末尾の改行を落とすため、ファイルの末尾の改行を補う（MD047 を項目に当てない）
            path.write_text(
                source.text if source.text.endswith("\n") else f"{source.text}\n", encoding="utf-8"
            )
            files.append(str(path))
        markdownlint = _run_cli(
            MARKDOWNLINT,
            [clis[MARKDOWNLINT], "--config", str(lint_dir / _MARKDOWNLINT_CONFIG), *files],
            lint_dir,
        )
        textlint = _run_cli(
            TEXTLINT,
            [
                clis[TEXTLINT],
                "--config",
                str(lint_dir / _TEXTLINT_CONFIG),
                "--format",
                "json",
                *files,
            ],
            lint_dir,
        )
    return _parse_markdownlint(markdownlint.stderr, sources) + _parse_textlint(
        textlint.stdout, sources
    )


def load_yamllint_config(lint_dir: Path, name: str = _YAMLLINT_CONFIG) -> YamlLintConfig:
    """lint のフォルダの yamllint の設定（既定は .yamllint.yaml）を読む。"""
    return YamlLintConfig(file=str(lint_dir / name))


def run_yamllint(path: PurePosixPath, text: str, config: YamlLintConfig) -> list[LintFinding]:
    """YAML のファイル 1 つに yamllint を当て、違反を返す。"""
    findings: list[LintFinding] = []
    for problem in linter.run(text, config, str(path)):  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        # YAML として読めない誤りは rule が None になる
        rule = cast("str | None", problem.rule) or _YAMLLINT_SYNTAX  # pyright: ignore[reportUnknownMemberType]
        level = cast("str", problem.level)  # pyright: ignore[reportUnknownMemberType]
        findings.append(
            LintFinding(
                path=path,
                line=cast("int", problem.line),  # pyright: ignore[reportUnknownMemberType]
                item_path=_WHOLE_FILE,
                tool="yamllint",
                rule=rule,
                message=cast("str", problem.desc),  # pyright: ignore[reportUnknownMemberType]
                warning=level == "warning",
            )
        )
    return findings
