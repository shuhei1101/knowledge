"""scripts/ の単体テストで共通に使う fixture。"""

import io
import sys
import textwrap
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest

# リポジトリの拡張したメタスキーマ
META_SCHEMA = (Path(__file__).resolve().parents[3] / "schemas/meta.schema.yaml").read_text(
    encoding="utf-8"
)

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
      - $ref: knowledge-common.schema.yaml#/$defs/metadata
    properties:
      kind:
        const: rule
      arguments:
        title: 引数
    """
)

# 規約の文書を docs/rule/ から引き、文書の違反の検査も当てる project-index.yaml
CONFIG_YAML = textwrap.dedent(
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

type RepoFactory = Callable[[Mapping[str, str]], Path]


@pytest.fixture
def repo_factory(tmp_path: Path) -> RepoFactory:
    """schemas/ と project-index.yaml と、渡した文書を持つリポジトリの直下を作る関数を返す。"""

    def _create(files: Mapping[str, str]) -> Path:
        root = tmp_path / "repo"
        (root / "schemas").mkdir(parents=True)
        (root / "docs").mkdir()
        (root / "schemas" / "knowledge-common.schema.yaml").write_text(
            COMMON_SCHEMA, encoding="utf-8"
        )
        (root / "schemas" / "rule.schema.yaml").write_text(RULE_SCHEMA, encoding="utf-8")
        (root / "schemas" / "meta.schema.yaml").write_text(META_SCHEMA, encoding="utf-8")
        (root / "project-index.yaml").write_text(CONFIG_YAML, encoding="utf-8")
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
