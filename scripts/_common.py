"""文書の YAML の読み込み・項目のパスと行の対応・違反の型・ファイルの並列の読み込み。

入口のスクリプト（knowledge_checks.py・knowledge_markdown.py・check_all.py・build_pages.py）が同じフォルダから import する。
"""

from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any, Protocol, TypedDict, cast

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import YAMLError
from ruamel.yaml.scalarstring import FoldedScalarString, LiteralScalarString

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from pathlib import Path

# スクリプトの起動から終わりまでの上限（秒）。dev-docs の 1 回の制限時間に収める
LIMIT_SEC = 20.0

# read_texts が並列に読むスレッドの数。/mnt/c の 259 件を 1 件ずつ読むと 3.4 秒、16 で 0.2 秒
READ_WORKERS = 16

# リポジトリの直下の dev-docs の配信の設定
CONFIG = "dev-docs.yaml"

type PathPart = str | int


class Violation(TypedDict):
    """dev-docs の validators の約束の違反 1 件。"""

    # 違反した項目のパス（items[3].body）。文書全体にかかるものは $
    path: str
    # 違反の内容。先頭に文書の行を「{行} 行目: 」で置く
    rule: str
    fix: str


class DocumentError(Exception):
    """YAML として読めないか、最上位がマッピングでない文書。"""

    def __init__(self, line: int, message: str) -> None:
        super().__init__(f"{line} 行目: {message}")
        # 読めなかった行（1 始まり）。行が分からないときは 1
        self.line = line
        self.message = message


class ConfigError(Exception):
    """dev-docs.yaml が無い・読めない・documents が配列でない。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class _LineCol(Protocol):
    """ruamel.yaml の .lc（キー・値・要素の 0 始まりの行と列）。"""

    def key(self, key: object) -> tuple[int, int]: ...

    def value(self, key: object) -> tuple[int, int]: ...

    def item(self, index: int) -> tuple[int, int]: ...


def _line_col(node: CommentedMap | CommentedSeq) -> _LineCol:
    """マッピング・配列の行と列の情報を返す。"""
    # ruamel.yaml は .lc に型を付けていないので、使う形の Protocol として引く
    return cast("_LineCol", getattr(node, "lc"))  # noqa: B009


def key_line(node: CommentedMap, key: object) -> int:
    """マッピングのキーの文書の行（1 始まり）を返す。"""
    return _line_col(node).key(key)[0] + 1


def value_line(node: CommentedMap, key: object) -> int:
    """マッピングの値の始まりの文書の行（1 始まり）を返す。"""
    return _line_col(node).value(key)[0] + 1


def item_line(node: CommentedSeq, index: int) -> int:
    """配列の要素の始まりの文書の行（1 始まり）を返す。"""
    return _line_col(node).item(index)[0] + 1


def as_mapping(value: object) -> Mapping[str, object] | None:
    """マッピングなら文字列のキーで引ける形で返す。マッピングでなければ None。"""
    if isinstance(value, Mapping):
        return cast("Mapping[str, object]", value)
    return None


def as_list(value: object) -> list[object] | None:
    """配列なら要素の型を object にして返す。配列でなければ None。"""
    if isinstance(value, list):
        return cast("list[object]", value)
    return None


def _load(yaml: YAML, text: str) -> object:
    """YAML を読む。ruamel.yaml の load は戻り値に型を付けていないので object にする。"""
    return cast("object", yaml.load(text))  # pyright: ignore[reportUnknownMemberType]


def load_safe(text: str) -> object:
    """行の情報の要らない YAML（スキーマなど）を安全な型だけで読む。"""
    return _load(YAML(typ="safe"), text)


def load_document(text: str) -> CommentedMap:
    """文書の YAML を行の情報つきのマッピングとして読む。"""
    try:
        data = _load(YAML(typ="rt"), text)
    except YAMLError as error:
        # 誤りの位置を持つ例外（MarkedYAMLError）は、その行と理由を使う
        mark: object = getattr(error, "problem_mark", None)
        line: object = getattr(mark, "line", None)
        problem: object = getattr(error, "problem", None)
        raise DocumentError(
            line + 1 if isinstance(line, int) else 1,
            problem if isinstance(problem, str) and problem else str(error),
        ) from error
    # 空の文書・配列・スカラーは文書として扱わない
    if not isinstance(data, CommentedMap):
        raise DocumentError(1, "最上位がマッピングではありません")
    return data


def format_path(parts: Sequence[PathPart]) -> str:
    """キーと添字の並びを dev-docs の項目のパスの書き方にする。"""
    if not parts:
        return "$"
    text = ""
    for part in parts:
        if isinstance(part, int):
            text += f"[{part}]"
        else:
            text += f".{part}" if text else part
    return text


def _string_line(line: int, value: str) -> int:
    """値の始まりの行から、本文の 1 行目の文書の行を求める。"""
    # | と > のブロックは、インジケーターの次の行から本文が始まる
    if isinstance(value, LiteralScalarString | FoldedScalarString):
        return line + 1
    return line


def iter_strings(
    node: CommentedMap | CommentedSeq, parts: tuple[PathPart, ...] = ()
) -> Iterator[tuple[tuple[PathPart, ...], int, str]]:
    """文書の中の全ての文字列の値を、項目のパスと本文の 1 行目の行で返す。"""
    if isinstance(node, CommentedMap):
        for key, value in cast("Mapping[object, object]", node).items():
            child = (*parts, key if isinstance(key, str) else str(key))
            # マッピング・配列は子へたどる
            if isinstance(value, CommentedMap | CommentedSeq):
                yield from iter_strings(value, child)
            # 文字列は値の位置から行を求める。数・真偽値・null は飛ばす
            elif isinstance(value, str):
                yield child, _string_line(value_line(node, key), value), value
        return
    for index, value in enumerate(cast("list[object]", node)):
        child = (*parts, index)
        if isinstance(value, CommentedMap | CommentedSeq):
            yield from iter_strings(value, child)
        elif isinstance(value, str):
            yield child, _string_line(item_line(node, index), value), value


def _read_text(path: Path) -> str | None:
    """ファイルを UTF-8 で読む。読めなければ None。"""
    try:
        return path.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return None


def read_texts(paths: Sequence[Path]) -> dict[Path, str | None]:
    """ファイルを並列に UTF-8 で読み、パス → 中身で返す。"""
    with ThreadPoolExecutor(max_workers=READ_WORKERS) as pool:
        texts = list(pool.map(_read_text, paths))
    return dict(zip(paths, texts, strict=True))


def line_of(doc: CommentedMap, parts: Sequence[PathPart]) -> int:
    """キーと添字の並びが指す項目の、文書の行（1 始まり）を返す。"""
    line = 1
    node: object = doc
    for part in parts:
        # マッピングのキー: キーの行を控えて子へ進む
        if isinstance(node, CommentedMap) and part in node:
            line = key_line(node, part)
            node = cast("Mapping[object, object]", node)[part]
        # 配列の添字: 要素の行を控えて子へ進む
        elif isinstance(node, CommentedSeq) and isinstance(part, int) and 0 <= part < len(node):
            line = item_line(node, part)
            node = cast("list[object]", node)[part]
        # たどれない: そこまでの最も深い行を使う
        else:
            break
    return line


def load_config(root: Path) -> list[Mapping[str, Any]]:
    """dev-docs.yaml の documents[] の行を読む。"""
    path = root / CONFIG
    if not path.is_file():
        message = f"{CONFIG} がありません"
        raise ConfigError(message)
    try:
        doc = load_document(path.read_text(encoding="utf-8"))
    except DocumentError as error:
        message = f"{CONFIG} の {error.line} 行目が読めません: {error.message}"
        raise ConfigError(message) from error
    documents = as_list(cast("Mapping[str, object]", doc).get("documents"))
    rows = [as_mapping(row) for row in documents] if documents is not None else [None]
    if not all(row is not None for row in rows):
        message = f"{CONFIG} に documents の配列がありません"
        raise ConfigError(message)
    return [row for row in rows if row is not None]


def strings(value: object) -> list[str]:
    """文字列の配列の値から文字列だけを返す。配列でなければ空。"""
    elements = as_list(value)
    if elements is None:
        return []
    return [element for element in elements if isinstance(element, str)]


def list_row_files(root: Path, row: Mapping[str, Any]) -> list[PurePosixPath]:
    """documents[] の 1 行の paths・exclude に当たるファイルを、リポジトリの直下からのパスで返す。"""
    if row.get("enabled") is False:
        return []
    exclude = strings(row.get("exclude"))
    files: set[PurePosixPath] = set()
    for pattern in strings(row.get("paths")):
        for file in root.glob(pattern):
            # ファイル名が exclude のどれかに当たるものを除く（dev-docs と同じ判定）
            if not file.is_file() or any(
                PurePosixPath(file.name).full_match(name) for name in exclude
            ):
                continue
            files.add(PurePosixPath(file.relative_to(root).as_posix()))
    return sorted(files)
