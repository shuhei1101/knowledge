# OBSのブラウザソース

OBS のブラウザソースで取り込む画面の前提のブラウザと、OBS 側・ページ側の作法。

## 前提のブラウザ

| 要素 | 決まり |
| --- | --- |
| 前提のブラウザ | OBS 同梱の Chromium。それより新しいブラウザの API は、機能の有無を確かめてから使う |
| バージョンの確かめ先 | OBS のバージョンと同梱の Chromium のバージョンの対応は書かない。[OBS のリリースノート](https://github.com/obsproject/obs-studio/releases)と、[obs-browser](https://github.com/obsproject/obs-browser) の CEF のバージョンで確かめる |

## OBS 側の設定

| 要素 | 決まり |
| --- | --- |
| ハードウェアアクセラレーション | ブラウザソースのハードウェアアクセラレーションを有効にする |
| フレームレート | カスタムフレームレートはオフにし、OBS の出力のフレームレートに合わせる。ハードウェアアクセラレーションが効かない構成では、カスタムフレームレートを出力のフレームレートと同じ値にする |
| 非表示の間 | 「表示されていないときにソースをシャットダウン」をオフにする |

## ページ側

| 要素 | 決まり |
| --- | --- |
| 背景 | `html` と `body` に不透明な背景を付けない（OBS が透過して重ねる） |
| 非表示の間 | `obsSourceVisibleChanged` を受け取り、非表示の間は演出のキューを止める |
| アニメーション | `transform` と `opacity` を基本にする |

## 出典

- [obs-browser](https://github.com/obsproject/obs-browser)
- [OBS の Browser Source の KB](https://obsproject.com/kb/browser-source)
- [Stick to Compositor-Only Properties and Manage Layer Count](https://web.dev/articles/stick-to-compositor-only-properties-and-manage-layer-count)
