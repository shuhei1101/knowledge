# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ruamel.yaml==0.19.1",
# ]
# ///
"""dev-docs.yaml の documents[] の visibility: public の文書を、mdmark の build で 1 枚の HTML にまとめる。

CI と手元から、リポジトリの直下で起動する。変換は converters[].run を子プロセスで呼び、
文書の ID への参照を、公開の文書なら 1 枚の中のリンク、それ以外なら master の YAML の URL に書き換える。

Usage:
# 公開の文書を _site/index.html にまとめる（_site は中身を消してから書く）
uv run --frozen --script scripts/build_pages.py --out _site
"""

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

from ruamel.yaml.error import YAMLError

from _common import (
    CONFIG,
    LIMIT_SEC,
    ConfigError,
    DocumentError,
    as_list,
    as_mapping,
    list_row_files,
    load_config,
    load_document,
    load_safe,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# npx で呼ぶ mdmark のバージョン
MDMARK_TAG = "v0.8.0"

# 公開しない文書への参照のリンクの頭
MASTER_BLOB_URL = "https://github.com/shuhei1101/knowledge/blob/master/"

# Pages のトップになる HTML
OUTPUT_HTML = "index.html"

# 一時フォルダに書く mdmark の設定のファイル名
_BUNDLE_CONFIG = "mdmark.config.yaml"

# overview の項目は見出しを持たない
_OVERVIEW_ID = "overview"

# 変換のスクリプトが項目の見出しにする深さ（group の段が無い項目）と、見出しの最大の深さ
_ITEM_HEADING = 2
_MAX_HEADING = 6

# group の段の区切り
_GROUP_SEPARATOR = " > "

# ATX の見出しの行（mdmark が見出しにする行と同じ）
_ATX_HEADING = re.compile(r"^(#{1,6})(?:\s+(.*?))?\s*$")

# コードブロックの囲み
_FENCE = re.compile(r"^\s*(```|~~~)")

# 見出しの ID から除く文字（文字・数字・_・-・空白のほか）
_SLUG_REMOVE = re.compile(r"[^\w\- ]")

# 文書の ID への参照（](id:{ID}) と ](id:{ID}#{項目})）
_REFERENCE = re.compile(r"\]\(id:([^)#\s]+)(?:#([^)\s]+))?\)")

# 終了コード。1 = 作れない成果物・想定していない例外、2 = 作り始めなかった
_EXIT_FAILED = 1
_EXIT_NOT_STARTED = 2


@dataclass(frozen=True)
class Source:
    """documents[] の変換の行から引いた文書 1 件と、参照の書き換えに使う値。"""

    # 文書の id
    id: str
    # リポジトリの直下からのパス
    path: PurePosixPath
    # visibility が public か
    public: bool
    # overview を除いた項目の（id、name、見出しの深さ）。文書の並び
    items: tuple[tuple[str, str, int], ...]
    # 行の converter が指す converters[].run
    run: tuple[str, ...]


class BuildError(Exception):
    """変換・参照の書き換え・mdmark の build のどれかが失敗した。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _use_utf8(stream: object) -> None:
    """標準出力・標準エラーを UTF-8 にする（Windows の既定のエンコーディングで書かない）。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """公開の文書を 1 枚の HTML にして出力のフォルダに置き、終了コードで合否を返す。"""
    parser = argparse.ArgumentParser(description="公開の文書を 1 枚の HTML にまとめる")
    parser.add_argument("--out", required=True, type=Path, help="出力のフォルダ")
    args = parser.parse_args(argv)
    out: Path = args.out
    _use_utf8(sys.stdout)
    _use_utf8(sys.stderr)

    try:
        root = Path.cwd()
        try:
            rows = load_config(root)
            converters = load_converters(root)
        except ConfigError as error:
            print(error.message, file=sys.stderr)
            return _EXIT_NOT_STARTED

        sources = list_sources(root, rows, converters)
        public = [source for source in sources if source.public]
        if not public:
            print("visibility: public の文書がありません", file=sys.stderr)
            return _EXIT_NOT_STARTED

        # 出力のフォルダは作り直し、失敗したときは空のまま残す
        shutil.rmtree(out, ignore_errors=True)
        out.mkdir(parents=True)

        with tempfile.TemporaryDirectory() as temp:
            workdir = Path(temp)
            # 全ての公開の文書を変換してから参照を書き換える（項目の見出しの ID を先に揃える）
            markdowns = {source.id: convert_source(root, source) for source in public}
            anchors = {
                source.id: item_anchors(markdowns[source.id], source.items) for source in public
            }
            index = {source.id: source for source in sources}
            names: list[str] = []
            for source in public:
                text = rewrite_references(markdowns[source.id], source, index, anchors)
                name = f"{source.id}.md"
                (workdir / name).write_text(text, encoding="utf-8")
                names.append(name)

            config = write_bundle_config(workdir, names)
            print(run_mdmark(config).rstrip("\n"))
            shutil.copyfile(workdir / OUTPUT_HTML, out / OUTPUT_HTML)
    except BuildError as error:
        print(error.message, file=sys.stderr)
        return _EXIT_FAILED
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返す
        traceback.print_exc()
        return _EXIT_FAILED
    else:
        return 0


def load_converters(root: Path) -> dict[str, tuple[str, ...]]:
    """dev-docs.yaml の converters[] を id → run にする。"""
    try:
        doc = load_document((root / CONFIG).read_text(encoding="utf-8"))
    except DocumentError as error:
        message = f"{CONFIG} の {error.line} 行目が読めません: {error.message}"
        raise ConfigError(message) from error
    converters: dict[str, tuple[str, ...]] = {}
    for row in as_list(cast("Mapping[str, object]", doc).get("converters")) or []:
        mapping = as_mapping(row)
        if mapping is None:
            continue
        converter_id = mapping.get("id")
        run = as_list(mapping.get("run"))
        # run が文字列の配列でない行は入れない
        if isinstance(converter_id, str) and run and all(isinstance(arg, str) for arg in run):
            converters[converter_id] = tuple(str(arg) for arg in run)
    return converters


def _items(value: object) -> tuple[tuple[str, str, int], ...]:
    """文書の items[] から、overview を除いた項目の（id、name、見出しの深さ）を引く。"""
    items: list[tuple[str, str, int]] = []
    for element in as_list(value) or []:
        item = as_mapping(element)
        if item is None:
            continue
        item_id = item.get("id")
        name = item.get("name")
        if not isinstance(item_id, str) or item_id == _OVERVIEW_ID or not isinstance(name, str):
            continue
        group = item.get("group")
        levels = group.split(_GROUP_SEPARATOR) if isinstance(group, str) and group.strip() else []
        # 変換のスクリプトは group の段の 1 つ下の深さを項目の見出しにする
        items.append((item_id, name, min(_ITEM_HEADING + len(levels), _MAX_HEADING)))
    return tuple(items)


def list_sources(
    root: Path,
    rows: Sequence[Mapping[str, Any]],
    converters: Mapping[str, tuple[str, ...]],
) -> list[Source]:
    """converter を持つ documents[] の行の文書を読み、参照の書き換えに使う値と並べて返す。"""
    sources: dict[PurePosixPath, Source] = {}
    for row in rows:
        converter = row.get("converter")
        # records の行と、変換のコマンドを引けない行は対象にしない
        if "records" in row or not isinstance(converter, str) or converter not in converters:
            continue
        for path in list_row_files(root, row):
            # 同じパスは最初に当たった行で 1 件にする
            if path in sources:
                continue
            try:
                doc = as_mapping(load_safe((root / path).read_text(encoding="utf-8")))
            except YAMLError as error:
                message = f"{path}: 文書の id を読めません"
                raise BuildError(message) from error
            doc_id = doc.get("id") if doc is not None else None
            if doc is None or not isinstance(doc_id, str):
                message = f"{path}: 文書の id を読めません"
                raise BuildError(message)
            sources[path] = Source(
                id=doc_id,
                path=path,
                public=doc.get("visibility") == "public",
                items=_items(doc.get("items")),
                run=converters[converter],
            )
    return list(sources.values())


def convert_source(root: Path, source: Source) -> str:
    """文書の YAML を変換のコマンドの標準入力へ渡し、標準出力の Markdown を返す。"""
    text = (root / source.path).read_text(encoding="utf-8")
    try:
        result = subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
            list(source.run),
            input=text,
            cwd=root,
            capture_output=True,
            encoding="utf-8",
            timeout=LIMIT_SEC,
            check=False,
        )
    except FileNotFoundError as error:
        message = f"{source.path}: 変換のコマンド {source.run[0]} がありません"
        raise BuildError(message) from error
    except subprocess.TimeoutExpired as error:
        message = f"{source.path}: 変換が {LIMIT_SEC} 秒で終わりませんでした"
        raise BuildError(message) from error
    if result.returncode != 0:
        message = (
            f"{source.path}: 変換のスクリプトが終了コード {result.returncode} で失敗しました\n"
            f"{result.stderr}"
        )
        raise BuildError(message)
    return result.stdout


def github_slug(text: str) -> str:
    """見出しの文字から、mdmark と同じ GitHub の規則の ID を作る。"""
    return _SLUG_REMOVE.sub("", text.strip().lower()).replace(" ", "-")


def item_anchors(markdown: str, items: Sequence[tuple[str, str, int]]) -> dict[str, str]:
    """変換した Markdown の見出しを文書の項目と突き合わせ、項目の id → 見出しの ID を返す。"""
    # コードブロックの外の見出しを、（深さ、文字、ID）で上から並べる
    headings: list[tuple[int, str, str]] = []
    counts: dict[str, int] = {}
    fence: str | None = None
    for line in markdown.splitlines():
        opened = _FENCE.match(line)
        if opened is not None:
            # 開いた囲みと同じ記号で閉じる
            if fence is None:
                fence = opened.group(1)
            elif opened.group(1) == fence:
                fence = None
            continue
        matched = _ATX_HEADING.match(line) if fence is None else None
        if matched is None:
            continue
        text = matched.group(2) or ""
        slug = github_slug(text)
        # 同じ ID の 2 つ目からは -1・-2 を付ける
        if slug in counts:
            counts[slug] += 1
            slug = f"{slug}-{counts[slug]}"
        else:
            counts[slug] = 0
        headings.append((len(matched.group(1)), text, slug))

    # 項目を順に、直前に対応づけた見出しより後の、同じ文字と深さの最初の見出しに対応づける
    anchors: dict[str, str] = {}
    start = 0
    for item_id, name, depth in items:
        for position in range(start, len(headings)):
            level, text, slug = headings[position]
            if level == depth and text == name:
                anchors[item_id] = slug
                start = position + 1
                break
    return anchors


def rewrite_references(
    markdown: str,
    source: Source,
    sources: Mapping[str, Source],
    anchors: Mapping[str, Mapping[str, str]],
) -> str:
    """Markdown の文書の ID への参照を、1 枚の中のリンクか master の YAML の URL に書き換える。"""

    def _replace(matched: re.Match[str]) -> str:
        target_id, item = matched.group(1), matched.group(2)
        target = sources.get(target_id)
        if target is None:
            message = f"{source.path}: 参照先の文書がありません: {target_id}"
            raise BuildError(message)
        # 公開しない文書: master の YAML へのリンク（項目は落とす）
        if not target.public:
            return f"]({MASTER_BLOB_URL}{target.path})"
        # 公開の文書: 項目の見出しがあればその見出しへ、無ければ文書へ（overview は見出しを持たない）
        anchor = anchors.get(target_id, {}).get(item) if item is not None else None
        if anchor is not None:
            return f"](./{target_id}.md#{anchor})"
        return f"](./{target_id}.md)"

    return _REFERENCE.sub(_replace, markdown)


def write_bundle_config(workdir: Path, names: Sequence[str]) -> Path:
    """一時フォルダに、公開の文書を並びのとおりまとめる mdmark の設定を書く。"""
    config = {
        "version": MDMARK_TAG,
        "build": {"include": list(names), "entry": names[0], "out": OUTPUT_HTML},
    }
    path = workdir / _BUNDLE_CONFIG
    # JSON は YAML として読める
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_mdmark(config: Path) -> str:
    """mdmark の build を起動し、標準出力を返す。"""
    try:
        result = subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
            [  # noqa: S607 - npx は Node のインストールで PATH から引く
                "npx",
                "-y",
                f"github:shuhei1101/mdmark#{MDMARK_TAG}",
                "build",
                "--config",
                str(config),
            ],
            cwd=config.parent,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
    except FileNotFoundError as error:
        message = "npx が PATH にありません。Node 24 以降を入れてください"
        raise BuildError(message) from error
    if result.returncode != 0:
        message = (
            f"mdmark の build が終了コード {result.returncode} で失敗しました\n{result.stderr}"
        )
        raise BuildError(message)
    # mdmark の警告はそのまま標準エラーへ出す
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.stdout


if __name__ == "__main__":
    sys.exit(main())
