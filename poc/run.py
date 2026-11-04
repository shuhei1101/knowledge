"""PoC: 文書の YAML の Markdown の項目に markdownlint・textlint を当て、違反の行を元の YAML の行で出す。"""

import collections
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from _common import format_path, iter_strings, load_document  # noqa: E402

POC = Path(__file__).resolve().parent
MDL_LINE = re.compile(r"^(?P<file>[^:]+\.md):(?P<line>\d+)(?::\d+)? (?:error|warning) (?P<rule>\S+) (?P<msg>.*)$")


def collect(paths: list[Path], out: Path) -> dict[str, tuple[Path, str, int]]:
    """Markdown の項目（キーが body の文字列）を 1 項目 1 ファイルで書き出し、ファイル名から元の位置を引く表を返す。"""
    table: dict[str, tuple[Path, str, int]] = {}
    for path in paths:
        doc = load_document(path.read_text(encoding="utf-8"))
        for parts, line, value in iter_strings(doc):
            if parts[-1] != "body":
                continue
            name = f"f{len(table):05d}.md"
            (out / name).write_text(value + "\n", encoding="utf-8")
            table[name] = (path, format_path(parts), line)
    return table


def run_markdownlint(out: Path) -> list[tuple[str, int, str, str]]:
    """markdownlint-cli2 の違反を (ファイル名, 行, ルール, 内容) で返す。"""
    proc = subprocess.run(
        [str(POC / "node_modules/.bin/markdownlint-cli2"), "--config", str(POC / ".markdownlint-cli2.jsonc"), "*.md"],
        cwd=out, capture_output=True, text=True, check=False,
    )
    rows = []
    for text in proc.stderr.splitlines():
        m = MDL_LINE.match(text)
        if m:
            rows.append((m["file"], int(m["line"]), m["rule"], m["msg"]))
    return rows


def run_textlint(out: Path) -> list[tuple[str, int, str, str]]:
    """textlint の違反を (ファイル名, 行, ルール, 内容) で返す。"""
    proc = subprocess.run(
        [str(POC / "node_modules/.bin/textlint"), "--config", str(POC / ".textlintrc.json"), "-f", "json", "."],
        cwd=out, capture_output=True, text=True, check=False,
    )
    rows = []
    for result in json.loads(proc.stdout or "[]"):
        for m in result["messages"]:
            rows.append((Path(result["filePath"]).name, m["line"], m["ruleId"], m["message"]))
    return rows


def main() -> int:
    """引数のファイル・フォルダの文書に当て、違反と集計を出す。"""
    paths = [p for a in sys.argv[1:] for p in (sorted(Path(a).rglob("*.yaml")) if Path(a).is_dir() else [Path(a)])]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        start = time.perf_counter()
        table = collect(paths, out)
        t_collect = time.perf_counter() - start
        mdl = run_markdownlint(out)
        t_mdl = time.perf_counter() - start - t_collect
        tl = run_textlint(out)
        t_tl = time.perf_counter() - start - t_collect - t_mdl
    counts: collections.Counter[str] = collections.Counter()
    for name, line, rule, msg in mdl + tl:
        path, item, base = table[name]
        counts[rule] += 1
        if len(paths) <= 3:
            # 項目の 1 行目が base の行。CLI の行は 1 始まり
            print(f"{path}:{base + line - 1}: {item}: {rule}: {msg}")
    print(f"文書 {len(paths)} 件・項目 {len(table)} 件・違反 {len(mdl) + len(tl)} 件")
    print(f"時間: 書き出し {t_collect:.1f}s・markdownlint {t_mdl:.1f}s・textlint {t_tl:.1f}s")
    for rule, n in counts.most_common():
        print(f"  {n:5d} {rule}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
