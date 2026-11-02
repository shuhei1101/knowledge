"""scripts/ の単体テストで共通に使う fixture。"""

import io
import json
import sys
import textwrap
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest

# 差し替えの maid が使う Python（テストを動かしている Python と同じ）
_PYTHON = sys.executable

# maid の差し替えのスクリプトの本体。引数を記録し、決めた出力と終了コードで終わる
_FAKE_MAID = textwrap.dedent(
    """\
    #!{python}
    import json
    import sys
    import time

    sys.stdin.read()
    record = {record!r}
    if record:
        with open(record, "a", encoding="utf-8") as f:
            f.write(json.dumps(sys.argv[1:]) + "\\n")
    time.sleep({sleep_sec!r})
    sys.stdout.write({stdout!r})
    sys.stderr.write({stderr!r})
    sys.exit({exit_code!r})
    """
)

# 正しい図と答える maid の標準出力
VALID_MAID_OUTPUT = json.dumps({"valid": True, "errors": []})

# 規約の文書のスキーマが $ref で指す共通のスキーマ
COMMON_SCHEMA = textwrap.dedent(
    """\
    $schema: https://json-schema.org/draft/2020-12/schema
    title: 共通
    $defs:
      metadata:
        type: object
        required:
          - id
          - kind
          - name
          - description
        properties:
          id:
            type: string
          kind:
            type: string
          name:
            type: string
          description:
            type: string
          items:
            type: array
    """
)

# 規約の文書のスキーマ
RULE_SCHEMA = textwrap.dedent(
    """\
    $schema: https://json-schema.org/draft/2020-12/schema
    title: 規約
    allOf:
      - $ref: common.schema.yaml#/$defs/metadata
    properties:
      kind:
        const: rule
      arguments:
        title: 引数
    """
)

# 規約の文書を docs/rule/ から引き、文書の違反の検査も当てる dev-docs.yaml
DEV_DOCS_YAML = textwrap.dedent(
    """\
    version: "3"
    name: knowledge
    documents:
      - id: rule
        paths:
          - docs/rule/*.yaml
        schema: schemas/rule.schema.yaml
        validators:
          - knowledge-checks
    """
)

type FakeMaidFactory = Callable[..., str]
type RepoFactory = Callable[[Mapping[str, str]], Path]


@pytest.fixture
def fake_maid_factory(tmp_path: Path) -> FakeMaidFactory:
    """決めた出力と終了コードで終わる maid の差し替えを作る関数を返す。"""
    created: list[Path] = []

    def _create(
        *,
        stdout: str = VALID_MAID_OUTPUT,
        exit_code: int = 0,
        stderr: str = "",
        sleep_sec: float = 0.0,
        record: Path | None = None,
    ) -> str:
        # 作るたびに別のフォルダに置き、名前を maid にする
        folder = tmp_path / f"maid-bin-{len(created)}"
        folder.mkdir()
        path = folder / "maid"
        path.write_text(
            _FAKE_MAID.format(
                python=_PYTHON,
                record=str(record) if record else "",
                sleep_sec=sleep_sec,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
            ),
            encoding="utf-8",
        )
        path.chmod(0o755)
        created.append(path)
        return str(path)

    return _create


@pytest.fixture
def repo_factory(tmp_path: Path) -> RepoFactory:
    """schemas/ と dev-docs.yaml と、渡した文書を持つリポジトリの直下を作る関数を返す。"""

    def _create(files: Mapping[str, str]) -> Path:
        root = tmp_path / "repo"
        (root / "schemas").mkdir(parents=True)
        (root / "docs").mkdir()
        (root / "schemas" / "common.schema.yaml").write_text(COMMON_SCHEMA, encoding="utf-8")
        (root / "schemas" / "rule.schema.yaml").write_text(RULE_SCHEMA, encoding="utf-8")
        (root / "dev-docs.yaml").write_text(DEV_DOCS_YAML, encoding="utf-8")
        # 渡したファイルで既定のファイルを上書きできる
        for relative, text in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    return _create


@pytest.fixture
def stdin_factory(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], None]:
    """標準入力を、渡した文字列を UTF-8 で読むストリームに差し替える関数を返す。"""

    def _set(text: str) -> None:
        monkeypatch.setattr(
            sys, "stdin", io.TextIOWrapper(io.BytesIO(text.encode("utf-8")), encoding="utf-8")
        )

    return _set
