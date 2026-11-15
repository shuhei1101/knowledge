# テスト実行方法の runner の層（TL-2・TL-3）をランナーで初めて回し、手元と skip の件数を突き合わせる

## 概要

開発者とエージェントが、knowledge の単体テスト（TL-2）と結合テスト（TL-3）を、手元と同じ結果になると確かめた状態で GitHub Actions のランナーで回せるようになる。

## 背景

[Issue #408](https://github.com/shuhei1101/knowledge/issues/408) の要望。
[PR #404](https://github.com/shuhei1101/knowledge/pull/404) で `.github/workflows/test.yml` と `run_runner` を追加したが、`workflow_dispatch` は既定ブランチ（develop）にある workflow だけを起動できるため、#404 の中ではランナーで回せなかった。
判定フローチャート『テストの実行場所』の ※4 は、runner にした層をランナーで回したときの skip の件数が手元と同じかを確認すると定めている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [CI](./CI.md) | CI の計画書 |
