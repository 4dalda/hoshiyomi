# 親近感版 ビジュアルレビュー

対象ソースは一つ上の `index.html`、検証内容は [REVIEW.md](../REVIEW.md) を参照してください。

## 最初に確認するもの

| 対象 | 初期表示 | スクロール途中 | シーン終端 | 録画 |
|---|---|---|---|---|
| PC 1440×900 | [画像](pc-hero.png) | [画像](pc-parallax.png) | [画像](1440-scene-end.png) | [MP4](pc-scroll.mp4) |
| スマホ相当390×844 | [画像](mobile-hero.png) | [画像](mobile-parallax.png) | [画像](390-scene-end.png) | [MP4](mobile-scroll.mp4) |

録画はダウンロードして再生できます。下方向・逆方向のホイール操作、次セクションへの移動、受付案内の表示を含みます。

## 続くセクション

- PC: [お悩み](pc-concerns.png) / [強み](pc-strengths.png)
- スマホ相当: [お悩み](mobile-concerns.png) / [強み](mobile-strengths.png)

## レビューポイント

1. スマホの人物サイズと余白のバランス。
2. 人物が上方向へ抜けていく構図、素材下端マスクの見え方。
3. PCの背景・光・人物・文字の速度差による奥行き。

修正済み: スマホのCTA・補足文と人物の重なり、人物の水平な切り抜き下端、カードの折り返し。

検証環境はローカルHTTP配信＋ヘッドレスChromiumです。スマホ実機・Safari・低速端末は未検証。`metrics.json` は実DOM計測、`verification.json` は往復・reduced-motionの検証、`playback.json` はMP4再生の検証です。

撮影スクリプトは検証時のローカルパスを含みます。再実行時は `url` と `out`、Chromiumのパスを環境に合わせて設定してください。
