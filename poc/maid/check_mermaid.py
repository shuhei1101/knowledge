"""PoC: 標準入力の YAML の文書から mermaid を取り出し、maid で --fix 無しで検査して違反の一覧の JSON を返す。"""
import json, re, shutil, subprocess, sys, time

import yaml

BUDGET_SEC = 20.0
FENCE = re.compile(r"^```mermaid\s*$")
OUTER = re.compile(r"^(````+)")


def blocks(node, path=""):
    """文字列の項目の中の mermaid のブロックを (項目のパス, 文書の開始行, 本文) で返す。"""
    if isinstance(node, yaml.MappingNode):
        for k, v in node.value:
            yield from blocks(v, f"{path}.{k.value}" if path else k.value)
    elif isinstance(node, yaml.SequenceNode):
        for i, v in enumerate(node.value):
            yield from blocks(v, f"{path}[{i}]")
    elif isinstance(node, yaml.ScalarNode) and "```mermaid" in str(node.value):
        base = node.start_mark.line + (1 if node.style in ("|", ">") else 0)
        lines = node.value.split("\n")
        i, outer = 0, None
        while i < len(lines):
            stripped = lines[i].strip()
            m = OUTER.match(stripped)
            if m and (outer is None or m.group(1) == outer):
                # 4 つ以上のバッククォートの囲みの中は記述例なので検査しない
                outer = None if outer else m.group(1)
            elif outer is None and FENCE.match(stripped):
                start, body = i + 1, []
                i += 1
                while i < len(lines) and lines[i].strip() != "```":
                    body.append(lines[i])
                    i += 1
                yield path, base + start + 1, "\n".join(body) + "\n"
            i += 1


def main() -> int:
    started = time.monotonic()
    maid = shutil.which("maid")
    if maid is None:
        print(json.dumps({"error": "maid が PATH から引けません"}, ensure_ascii=False), file=sys.stderr)
        return 2
    root = yaml.compose(sys.stdin.read())
    violations = []
    for item, doc_line, body in blocks(root):
        left = BUDGET_SEC - (time.monotonic() - started)
        if left <= 0:
            violations.append({"item": item, "line": doc_line, "message": "時間切れで検査できませんでした"})
            continue
        res = subprocess.run([maid, "-", "--format", "json"], input=body, capture_output=True, text=True, timeout=left)
        for e in json.loads(res.stdout).get("errors", []):
            violations.append({"item": item, "line": doc_line + e["line"] - 1, "column": e["column"], "code": e.get("code"), "message": e["message"]})
    print(json.dumps({"violations": violations}, ensure_ascii=False))
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
