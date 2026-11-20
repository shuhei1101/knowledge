# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "ruamel.yaml==0.19.1",
# ]
# ///
"""標準入力のネットミーム 1 件に、スキーマで見られない決まりを当て、違反の配列の JSON を標準出力へ出す。

project-index の validators の meme-checks。指す作品の実在・内容の分類のタグ・作品のタグの一致を検査する。
作業ディレクトリはネットミームの配信元（memes/）の直下にする。

Usage:
# ネットミーム 1 件を検査する
uv run --frozen --script scripts/meme_checks.py < memes/kusuriya-dokudesu.yaml
"""

import argparse
import io
import json
import sys
import traceback
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import MarkedYAMLError, YAMLError

# ネットミームがちょうど 1 つ持つ内容の分類のタグ
CONTENT_TAGS = (
    "topic:セリフ",
    "topic:タイトル",
    "topic:キャラクター",
    "topic:用語",
    "topic:題材",
    "topic:口癖",
    "topic:呼び名",
)

# 配信元の直下からの作品のフォルダ
WORKS_DIR = Path("works")


def _use_utf8(stream: object) -> None:
    """標準入出力を UTF-8 にする（Windows の既定のエンコーディングで読み書きしない）。"""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """標準入力のネットミームを検査し、違反の配列の JSON を標準出力へ出す。"""
    parser = argparse.ArgumentParser(description="標準入力のネットミーム 1 件の違反を出す")
    parser.parse_args(argv)
    _use_utf8(sys.stdin)
    _use_utf8(sys.stdout)
    try:
        violations = check_meme(sys.stdin.read(), Path.cwd())
    except Exception:  # noqa: BLE001 - 想定していない例外は traceback を出して終了コードで返す
        traceback.print_exc()
        return 1
    print(json.dumps(violations, ensure_ascii=False))
    return 0


def check_meme(text: str, root: Path) -> list[dict[str, str]]:
    """ネットミーム 1 件に全ての検査を当て、指す作品・内容の分類のタグ・作品のタグの順の違反を返す。"""
    try:
        doc = cast("object", YAML(typ="rt").load(text))  # pyright: ignore[reportUnknownMemberType]
    except YAMLError as error:
        mark = cast("object", error.problem_mark) if isinstance(error, MarkedYAMLError) else None  # pyright: ignore[reportUnknownMemberType]
        line = cast("int", getattr(mark, "line", 0)) + 1
        return [
            {
                "path": "$",
                "rule": f"{line} 行目: YAML として読めません: {error}",
                "fix": "YAML の文法の誤りを修正する",
            }
        ]
    # 最上位がマッピングでない入力は、スキーマの検査が違反を出す
    if not isinstance(doc, CommentedMap):
        return []

    works = load_works(root)
    work = cast("object", doc.get("work"))  # pyright: ignore[reportUnknownMemberType]
    tags = _tag_names(cast("object", doc.get("tags")))  # pyright: ignore[reportUnknownMemberType]
    violations: list[dict[str, str]] = []

    # 作品を指していて、その作品が works/ に無い
    if isinstance(work, str) and work not in works:
        violations.append(
            {
                "path": "work",
                "rule": f"{_line(doc, 'work')} 行目: 作品 `{work}` が works/ にありません",
                "fix": "先に作品を登録するか、登録済みの作品の ID を指す",
            }
        )

    # 内容の分類のタグがちょうど 1 つでない
    content = [tag for tag in tags if tag in CONTENT_TAGS]
    if len(content) != 1:
        violations.append(
            {
                "path": "tags",
                "rule": (
                    f"{_line(doc, 'tags')} 行目: 内容の分類のタグ（{'・'.join(CONTENT_TAGS)}）を"
                    f"ちょうど 1 つ持つ必要があります。持っているのは {'・'.join(content) or 'なし'}"
                ),
                "fix": "内容の分類のタグを 1 つだけ付ける",
            }
        )

    # 実在する作品を指していて、作品のタグがネットミームに無い
    if isinstance(work, str) and work in works:
        missing = [tag for tag in works[work] if tag not in tags]
        if missing:
            violations.append(
                {
                    "path": "tags",
                    "rule": (
                        f"{_line(doc, 'tags')} 行目: 作品 `{work}` のタグ "
                        f"{'・'.join(missing)} がありません"
                    ),
                    "fix": "作品と同じタグを付ける",
                }
            )
    return violations


def load_works(root: Path) -> dict[str, tuple[str, ...]]:
    """配信元の作品から、作品の ID → タグの名前の索引を作る。"""
    folder = root / WORKS_DIR
    # 作品のフォルダが無い: 作品は 0 件
    if not folder.is_dir():
        return {}
    works: dict[str, tuple[str, ...]] = {}
    for path in sorted(folder.glob("*.yaml")):
        try:
            doc = cast("object", YAML(typ="safe").load(path.read_text(encoding="utf-8")))  # pyright: ignore[reportUnknownMemberType]
        except OSError, UnicodeDecodeError, YAMLError:
            # 読めない作品の違反は、その作品を検査するときに出る
            continue
        # id を持たない作品は索引に入れない
        if not isinstance(doc, Mapping):
            continue
        work = cast("Mapping[str, object]", doc)
        work_id = work.get("id")
        if not isinstance(work_id, str):
            continue
        works[work_id] = _tag_names(work.get("tags"))
    return works


def _tag_names(value: object) -> tuple[str, ...]:
    """tags[] の要素の文字列の name を並べる。"""
    if not isinstance(value, Sequence) or isinstance(value, str):
        return ()
    names: list[str] = []
    for item in cast("Sequence[object]", value):
        # name の文字列を持つ要素だけを並べる
        name = cast("Mapping[str, object]", item).get("name") if isinstance(item, Mapping) else None
        if isinstance(name, str):
            names.append(name)
    return tuple(names)


def _line(doc: CommentedMap, key: str) -> int:
    """キーの行（1 始まり）を返す。キーが無ければ 1 行目にする。"""
    if key not in doc:
        return 1
    return cast("tuple[int, int]", doc.lc.key(key))[0] + 1  # pyright: ignore[reportUnknownMemberType]


if __name__ == "__main__":
    sys.exit(main())
