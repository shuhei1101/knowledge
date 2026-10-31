"""mermaid の文法を検査する maid の、PATH からの在りかの確認と打ち切りつきの呼び出し。

knowledge_checks.py・check_all.py が同じフォルダから import する。
"""

import json
import shutil
import subprocess
from dataclasses import dataclass
from typing import cast

# PATH から引く maid のコマンド名
MAID = "maid"

# 残り時間がこれより短ければ maid を呼ばずに時間切れにする（秒）。Linux 側の maid の 1 文書の最大 0.90 秒を上回る値
MIN_REMAINING_SEC = 1.0

# maid の終了コード。0 = 誤りなし、1 = 誤りあり。それ以外は maid 自身の失敗
_EXIT_CODES = (0, 1)

# maid の出力が読めないときの理由
_UNREADABLE = "maid の出力を読めません"


@dataclass(frozen=True)
class MaidFinding:
    """maid が返した誤り 1 件。"""

    # 渡した図の中の行（1 始まり）
    line: int
    message: str


class MaidOutputError(Exception):
    """maid の標準出力が JSON として読めないか、終了コードが 0・1 でない。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def find_maid() -> str | None:
    """PATH から maid の実行ファイルを引く。"""
    return shutil.which(MAID)


def run_maid(executable: str, diagram: str, timeout_sec: float) -> list[MaidFinding]:
    """mermaid の図 1 つを maid に標準入力で渡し、誤りを返す。"""
    # --fix を付けないので入力を書き換えない。打ち切りを超えると subprocess.TimeoutExpired を送出する
    result = subprocess.run(  # noqa: S603 - 引数は配列で渡し、シェルを通さない
        [executable, "-", "--format", "json"],
        input=diagram,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout_sec,
        check=False,
    )
    # 0・1 以外は maid 自身の失敗: 標準エラーの最後の行を理由にする
    if result.returncode not in _EXIT_CODES:
        lines = result.stderr.strip().splitlines()
        last = lines[-1] if lines else ""
        message = f"maid が終了コード {result.returncode} で終わりました: {last}"
        raise MaidOutputError(message)
    try:
        data: object = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise MaidOutputError(_UNREADABLE) from error
    errors = cast("dict[str, object]", data).get("errors") if isinstance(data, dict) else None
    if not isinstance(errors, list):
        raise MaidOutputError(_UNREADABLE)
    findings: list[MaidFinding] = []
    for error in cast("list[object]", errors):
        # line と message を持たない要素は出力の形の違いとして扱う
        if not isinstance(error, dict):
            raise MaidOutputError(_UNREADABLE)
        line = cast("dict[str, object]", error).get("line")
        text = cast("dict[str, object]", error).get("message")
        if not isinstance(line, int) or not isinstance(text, str):
            raise MaidOutputError(_UNREADABLE)
        findings.append(MaidFinding(line=line, message=text))
    return findings
