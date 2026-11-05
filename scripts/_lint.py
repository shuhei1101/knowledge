"""全ての文書の検査で当てる markdownlint-cli2・textlint・yamllint の、在りかの確認と呼び出しと違反の行の対応。

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

from _common import DocumentError, format_path, iter_strings, load_document

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

type LintTool = Literal["markdownlint", "textlint", "yamllint"]


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


def load_yamllint_config(lint_dir: Path) -> YamlLintConfig:
    """lint のフォルダの .yamllint.yaml を読む。"""
    return YamlLintConfig(file=str(lint_dir / _YAMLLINT_CONFIG))


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
