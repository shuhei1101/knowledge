"""文書の違反の検査（scripts/knowledge_checks.py）の結合テスト。"""

import hashlib
import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

from _common import MDMARK_REF

# conftest の fixture の型。子プロセスの結果は conftest の Completed
type RunScript = Callable[..., Any]
type RepoFactory = Callable[[dict[str, str]], Path]

# 項目 x を持つ配信元の文書
_DOC_A = "id: a\nkind: rule\nname: A\ndescription: A の文書\nitems:\n  - id: x\n    name: X\n    body: 本文\n"


def _hashes(root: Path) -> dict[str, str]:
    """フォルダの配下の全てのファイルのハッシュを返す。"""
    return {
        str(file.relative_to(root)): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in sorted(root.rglob("*"))
        if file.is_file()
    }


def test_normal(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """違反の無い文書に空の配列を返す（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/a.yaml": _DOC_A})
    before = _hashes(root)
    stdin = (
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: |-\n"
        "      [A](id:a#x)\n"
        "related:\n"
        "  - to: a\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []
    assert _hashes(root) == before


def test_normal_when_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """項目の ID の重複・参照切れを全て配列で返す（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/a.yaml": _DOC_A})
    stdin = (
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: 本文。\n"
        "  - id: p\n"
        "    body: 本文。\n"
        "  - id: q\n"
        "    body: '[B](id:missing)'\n"
        "related:\n"
        "  - to: missing\n"
        "    type: references\n"
        "    when: いつでも\n"
    )
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [v["path"] for v in violations] == [
        "items[1].id",
        "items[2].body",
        "related[0].to",
    ]


def test_normal_when_word_list_examples_fail(
    run_script: RunScript, repo_factory: RepoFactory
) -> None:
    """対応表の行の examples が照合と合わなければ、1 件 1 違反で返す（正常系）。"""
    # 準備
    root = repo_factory({})
    (root / "docs" / "word-list").mkdir()
    stdin = (
        "id: self\n"
        "kind: word-list\n"
        "entries:\n"
        "  - id: naosu\n"
        "    ng: 直す\n"
        "    ok: [修正]\n"
        "    pattern: 直す\n"
        "    examples:\n"
        "      hit: [直した]\n"
        "      pass: [修正]\n"
        "  - id: katachi\n"
        "    ng: 形\n"
        "    ok: [構造]\n"
        "    pattern: 形\n"
        "    examples:\n"
        "      hit: [この形]\n"
        "      pass: [形式]\n"
        "  - id: broken\n"
        "    ng: 形\n"
        "    ok: [構造]\n"
        "    pattern: 形(\n"
        "    examples:\n"
        "      hit: [形]\n"
        "      pass: [形式]\n"
    )
    lines = stdin.splitlines()
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert [violation["path"] for violation in violations] == [
        "entries[0].examples.hit[0]",
        "entries[1].examples.pass[0]",
        "entries[2].pattern",
    ]
    # rule の先頭の行番号が、文書の中の該当する行を指す
    for violation, text in zip(violations, ["直した", "形式", "形("], strict=True):
        number = int(violation["rule"].split(" 行目")[0])
        assert text in lines[number - 1]


# docs/rule/*.yaml の行が alias_type を持ち、docs/word-list/*.yaml の行は持たない project-index.yaml
_ALIAS_CONFIG = (
    'version: "3"\n'
    "name: knowledge\n"
    "documents:\n"
    "  - id: rule\n"
    "    paths: [docs/rule/*.yaml]\n"
    "    alias_type: doc\n"
    "  - id: word-list\n"
    "    paths: [docs/word-list/*.yaml]\n"
)


def test_normal_when_aliases_collide(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """ほかの文書の name・aliases と正規化して一致する aliases を、1 件 1 違反で返す（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "project-index.yaml": _ALIAS_CONFIG,
            "docs/rule/a.yaml": "id: a\nname: Alpha 規約\naliases:\n  - アルファ\n",
            # 書き込む前の b
            "docs/rule/b.yaml": "id: b\nname: B\naliases:\n  - ベータ\n",
            "docs/word-list/w.yaml": "id: w\nname: 単語表\n",
        }
    )
    stdin = (
        "id: b\nname: B\naliases:\n  - ' ａｌｐｈａ 規約 '\n  - アルファ\n  - ベータ\n  - 単語表\n"
    )
    lines = stdin.splitlines()
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert [violation["path"] for violation in violations] == ["aliases[0]", "aliases[1]"]
    assert "`a` の name" in violations[0]["rule"]
    assert "`a` の aliases" in violations[1]["rule"]
    # rule の先頭の行番号が、文書の中の該当する行を指す
    for violation, text in zip(violations, ["ａｌｐｈａ", "アルファ"], strict=True):
        number = int(violation["rule"].split(" 行目")[0])
        assert text in lines[number - 1]


# 規約の行（alias_type: doc）と用語集の行（records: terms・alias_type: term）を持つ project-index.yaml
_TERMS_CONFIG = (
    'version: "3"\n'
    "name: knowledge\n"
    "documents:\n"
    "  - id: rule\n"
    "    paths: [docs/rule/*.yaml]\n"
    "    alias_type: doc\n"
    "  - id: terms\n"
    "    paths: [docs/terms.yaml]\n"
    "    records: terms\n"
    "    alias_type: term\n"
)


def test_normal_when_aliases_collide_with_terms(
    run_script: RunScript, repo_factory: RepoFactory
) -> None:
    """records を持つ行の文書は、要素ごとの name・aliases を照合の相手にする（正常系）。"""
    # 準備
    root = repo_factory(
        {
            "project-index.yaml": _TERMS_CONFIG,
            "docs/terms.yaml": (
                "id: terms\n"
                "name: 用語集\n"
                "terms:\n"
                "  - id: ai-slop\n"
                "    name: AI slop\n"
                "    aliases:\n"
                "      - AI らしい単語\n"
            ),
        }
    )
    stdin = "id: b\nname: B\naliases:\n  - AI らしい単語\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert [violation["path"] for violation in violations] == ["aliases[0]"]
    assert "`ai-slop` の aliases" in violations[0]["rule"]


def test_normal_when_aliases_duplicate(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """自分の name か前の aliases と正規化して一致する aliases を、1 件 1 違反で返す（正常系）。"""
    # 準備
    root = repo_factory({"project-index.yaml": _ALIAS_CONFIG, "docs/rule/a.yaml": _DOC_A})
    stdin = "id: b\nname: Beta 規約\naliases:\n  - ベータ\n  - ' ｂｅｔａ 規約 '\n  - べーた\n  - ' ベータ '\n"
    lines = stdin.splitlines()
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert [violation["path"] for violation in violations] == ["aliases[1]", "aliases[3]"]
    assert "name" in violations[0]["rule"]
    assert "aliases[0]" in violations[1]["rule"]
    # rule の先頭の行番号が、文書の中の該当する行を指す
    assert violations[0]["rule"].startswith("5 行目: ")
    assert "ｂｅｔａ 規約" in lines[4]
    assert violations[1]["rule"].startswith("7 行目: ")
    assert " ベータ " in lines[6]


def test_normal_when_config_missing(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """project-index.yaml が無ければ aliases を照合せず、path: $ の違反とほかの検査の違反を返す（正常系）。"""
    # 準備
    root = repo_factory({"docs/rule/a.yaml": _DOC_A})
    (root / "project-index.yaml").unlink()
    stdin = "id: self\naliases:\n  - アルファ\nitems:\n  - id: p\n    body: '[B](id:missing)'\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert sorted(violation["path"] for violation in violations) == ["$", "items[0].body"]
    config = next(violation for violation in violations if violation["path"] == "$")
    assert "project-index.yaml" in config["rule"]


def test_normal_when_invalid_yaml(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """読めない入力を path: $ の違反 1 件で返す（正常系）。"""
    # 準備
    root = repo_factory({})
    stdin = "items:\n  - id: a\n    name: [\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert len(violations) == 1
    assert violations[0]["path"] == "$"
    assert " 行目: " in violations[0]["rule"]


# docs/checksheet/*.yaml の行だけを持つ project-index.yaml
_CHECKSHEET_CONFIG = (
    'version: "3"\n'
    "name: knowledge\n"
    "validators:\n"
    "  - id: knowledge-checks\n"
    "    run: [uv, run, --frozen, --script, scripts/knowledge_checks.py]\n"
    "    on: [write]\n"
    "documents:\n"
    "  - id: checksheet\n"
    "    paths:\n"
    "      - docs/checksheet/*.yaml\n"
    "    schema: schemas/checksheet.schema.yaml\n"
    "    validators:\n"
    "      - knowledge-checks\n"
)


def test_normal_when_aspect_ids_duplicate(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """チェックシートの観点の要素の ID の重複を、後に出た要素の違反にする（正常系）。"""
    # 準備
    root = repo_factory({"project-index.yaml": _CHECKSHEET_CONFIG})
    stdin = (
        "id: checksheet-review-common\n"
        "kind: checksheet\n"
        "items:\n"
        "  - id: overview\n"
        "    body: 概要。\n"
        "aspects:\n"
        "  - id: aspect-review-common-01\n"
        "    name: A\n"
        "  - id: aspect-review-common-01\n"
        "    name: B\n"
        "  - id: aspect-review-common-02\n"
        "    name: C\n"
    )
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    assert result.exit_code == 0
    violations = json.loads(result.stdout)
    assert [violation["path"] for violation in violations] == ["aspects[1].id"]
    assert "aspects[0]" in violations[0]["rule"]
    assert violations[0]["rule"].startswith("9 行目: ")


# scripts/lint/ の node_modules（textlint の本体とルール）
_LINT_DIR = Path(__file__).resolve().parents[3] / "scripts/lint"
_LINT_MODULES = _LINT_DIR / "node_modules"


def _copy_lint_configs(lint_dir: Path, names: list[str]) -> None:
    """scripts/lint/ の設定ファイルを、差し替えの lint のフォルダへコピーする。"""
    for name in names:
        shutil.copy(_LINT_DIR / name, lint_dir / name)


def test_normal_when_textlint_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """Markdown の項目の textlint の error の違反を、元の文書の行の違反で返す（正常系）。"""
    # 準備
    root = repo_factory({})
    before = _hashes(root)
    stdin = (
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: |-\n"
        "      概要です。\n"
        "      これはテストのためにここにある文で、助詞が重なるかを確かめるための文です。\n"
    )
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [violation["path"] for violation in violations] == ["items[0].body"]
    assert violations[0]["rule"].startswith(
        "6 行目: textlint/ja-technical-writing/no-doubled-joshi: "
    )
    assert _hashes(root) == before


def test_normal_when_textlint_warning_only(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """警告にしたルールの違反は返さず、空の配列を返す（正常系）。"""
    # 準備
    root = repo_factory({})
    # 既定の設定は警告にするルールを持たないため、one-sentence-per-line だけを警告にした lint のフォルダを作る
    lint_dir = tmp_path / "lint"
    lint_dir.mkdir()
    (lint_dir / ".textlintrc.json").write_text(
        '{"rules": {"one-sentence-per-line": {"severity": "warning"}}}\n', encoding="utf-8"
    )
    _copy_lint_configs(
        lint_dir, [".markdownlint-cli2.jsonc", "no-inline-strong.mjs", ".yamllint.yaml"]
    )
    (lint_dir / "node_modules").symlink_to(_LINT_MODULES)
    stdin = "id: self\nitems:\n  - id: p\n    body: A です。B です。\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin, args=["--lint-dir", str(lint_dir)])
    # 検証
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []


def test_normal_when_textlint_missing(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """textlint が見つからなければ、path: $ の違反 1 件とほかの検査の違反を返す（正常系）。"""
    # 準備
    root = repo_factory({})
    lint_dir = tmp_path / "lint"
    lint_dir.mkdir()
    (lint_dir / ".textlintrc.json").write_text('{"rules": {}}\n', encoding="utf-8")
    _copy_lint_configs(lint_dir, [".yamllint.yaml"])
    stdin = "id: self\nitems:\n  - id: p\n    body: '[B](id:missing)'\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin, args=["--lint-dir", str(lint_dir)])
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [violation["path"] for violation in violations] == ["items[0].body", "$"]
    assert "markdownlint-cli2" in violations[1]["rule"]
    assert "textlint" in violations[1]["rule"]
    assert str(lint_dir) in violations[1]["rule"]
    assert "npm ci --prefix scripts/lint" in violations[1]["fix"]


def test_normal_when_textlint_fails(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """textlint の終了コードが 0・1 でなければ、path: $ の違反 1 件を返す（正常系）。"""
    # 準備
    root = repo_factory({})
    lint_dir = tmp_path / "lint"
    bin_dir = lint_dir / "node_modules" / ".bin"
    bin_dir.mkdir(parents=True)
    (lint_dir / ".textlintrc.json").write_text('{"rules": {}}\n', encoding="utf-8")
    textlint = bin_dir / "textlint"
    textlint.write_text("#!/bin/sh\necho 設定を読めません >&2\nexit 2\n", encoding="utf-8")
    textlint.chmod(0o700)
    markdownlint = bin_dir / "markdownlint-cli2"
    markdownlint.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    markdownlint.chmod(0o700)
    _copy_lint_configs(lint_dir, [".markdownlint-cli2.jsonc", ".yamllint.yaml"])
    stdin = "id: self\nitems:\n  - id: p\n    body: 本文です。\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin, args=["--lint-dir", str(lint_dir)])
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [violation["path"] for violation in violations] == ["$"]
    assert "終了コード 2" in violations[0]["rule"]
    assert "設定を読めません" in violations[0]["rule"]


def test_normal_when_markdownlint_violations(
    run_script: RunScript, repo_factory: RepoFactory
) -> None:
    """Markdown の項目の markdownlint-cli2 の error の違反を元の文書の行の違反で返す（正常系）。"""
    # 準備
    root = repo_factory({})
    stdin = (
        "id: self\n"
        "items:\n"
        "  - id: p\n"
        "    body: |-\n"
        "      本文です。\n"
        "\n"
        "      ##  見出し\n"
        "\n"
        "      本文です。\n"
    )
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [violation["path"] for violation in violations] == ["items[0].body"]
    assert violations[0]["rule"].startswith("7 行目: markdownlint/MD019: ")


def test_normal_when_markdownlint_fails(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """markdownlint-cli2 の終了コードが 0・1 でなければ、path: $ の違反 1 件を返す（正常系）。"""
    # 準備
    root = repo_factory({})
    lint_dir = tmp_path / "lint"
    bin_dir = lint_dir / "node_modules" / ".bin"
    bin_dir.mkdir(parents=True)
    markdownlint = bin_dir / "markdownlint-cli2"
    markdownlint.write_text("#!/bin/sh\necho 設定を読めません >&2\nexit 2\n", encoding="utf-8")
    markdownlint.chmod(0o700)
    textlint = bin_dir / "textlint"
    textlint.write_text("#!/bin/sh\necho '[]'\nexit 0\n", encoding="utf-8")
    textlint.chmod(0o700)
    _copy_lint_configs(lint_dir, [".textlintrc.json", ".markdownlint-cli2.jsonc", ".yamllint.yaml"])
    stdin = "id: self\nitems:\n  - id: p\n    body: 本文です。\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin, args=["--lint-dir", str(lint_dir)])
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [violation["path"] for violation in violations] == ["$"]
    assert "markdownlint-cli2" in violations[0]["rule"]
    assert "終了コード 2" in violations[0]["rule"]
    assert "設定を読めません" in violations[0]["rule"]


def test_normal_when_yamllint_violations(run_script: RunScript, repo_factory: RepoFactory) -> None:
    """文書の YAML の yamllint の error の違反をファイル全体の違反で返す（正常系）。"""
    # 準備
    root = repo_factory({})
    stdin = "#コメント\nid: self\nitems:\n  - id: p\n    body: 本文です。\n"
    # 実行
    result = run_script("knowledge_checks", root, stdin)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [violation["path"] for violation in violations] == ["-"]
    assert violations[0]["rule"].startswith("1 行目: yamllint/comments: ")


# map の範囲に Mermaid として解釈できる flowchart を 2 つ持つ（mdmark の map_invalid）文書
_MAP_INVALID_DOC = (
    "id: self\n"
    "items:\n"
    "  - id: p\n"
    "    body: |-\n"
    "      <!-- map -->\n"
    "\n"
    "      ```mermaid\n"
    "      flowchart LR\n"
    "        a --> b\n"
    "      ```\n"
    "\n"
    "      ```mermaid\n"
    "      flowchart LR\n"
    "        c --> d\n"
    "      ```\n"
    "\n"
    "      <!-- /map -->\n"
)

# map の範囲に flowchart を 1 つ持つ、ほかの違反の無い文書
_MAP_DOC = (
    "id: self\n"
    "items:\n"
    "  - id: p\n"
    "    body: |-\n"
    "      <!-- map -->\n"
    "\n"
    "      ```mermaid\n"
    "      flowchart LR\n"
    "        a --> b\n"
    "      ```\n"
    "\n"
    "      <!-- /map -->\n"
)


def _mdmark_shim(folder: Path) -> Path:
    """MDMARK_REF の mdmark を npx で起動する mdmark を置いたフォルダを返す（ランナーの PATH に mdmark が無いため）。"""
    folder.mkdir(parents=True)
    shim = folder / "mdmark"
    shim.write_text(
        f'#!/bin/sh\nexec npx -y github:shuhei1101/mdmark#{MDMARK_REF} "$@"\n', encoding="utf-8"
    )
    shim.chmod(0o700)
    return folder


def test_normal_when_map_violations(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """map を含む項目の mdmark の map のずれを元の文書の行の違反で返す（正常系）。"""
    # 準備
    root = repo_factory({})
    folder = _mdmark_shim(tmp_path / "bin")
    # 実行
    result = run_script("knowledge_checks", root, _MAP_INVALID_DOC, path_prefix=folder)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [violation["path"] for violation in violations] == ["items[0].body"]
    # 行は items[0].body の 1 行目（<!-- map --> の行）
    assert violations[0]["rule"].startswith("5 行目: mdmark/map_invalid: ")


def test_normal_when_mdmark_missing(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """map を含む項目があり mdmark の CLI が PATH に無ければ、path: $ の違反 1 件を返す（正常系）。"""
    # 準備
    root = repo_factory({})
    folder = tmp_path / "bin"
    folder.mkdir()
    # node（markdownlint-cli2・textlint が使用する）と uv だけを置き、mdmark を置かない
    for name in ("node", "uv"):
        found = shutil.which(name)
        assert found is not None
        (folder / name).symlink_to(found)
    # 実行
    result = run_script("knowledge_checks", root, _MAP_DOC, path=str(folder))
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [violation["path"] for violation in violations] == ["$"]
    assert "mdmark の CLI" in violations[0]["rule"]
    assert "npm install -g github:shuhei1101/mdmark#develop" in violations[0]["fix"]


def test_normal_when_map_check_fails(
    run_script: RunScript, repo_factory: RepoFactory, tmp_path: Path
) -> None:
    """mdmark の終了コードが 0・1 でなければ、path: $ の違反 1 件を返す（正常系）。"""
    # 準備
    root = repo_factory({})
    folder = tmp_path / "bin"
    folder.mkdir()
    mdmark = folder / "mdmark"
    mdmark.write_text("#!/bin/sh\necho 点検できません >&2\nexit 2\n", encoding="utf-8")
    mdmark.chmod(0o700)
    # 実行
    result = run_script("knowledge_checks", root, _MAP_DOC, path_prefix=folder)
    # 検証
    violations = json.loads(result.stdout)
    assert result.exit_code == 0
    assert [violation["path"] for violation in violations] == ["$"]
    assert "終了コード 2" in violations[0]["rule"]
    assert "点検できません" in violations[0]["rule"]
