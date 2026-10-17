# logger.ts

ログ出力を集約する。画面・共通層は `console.*` を直書きせず logger 経由で出す。
- レベル（error / warn / info / debug）で出し分ける。
