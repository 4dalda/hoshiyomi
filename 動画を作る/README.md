# 動画を作る — 使い方

## 準備（初回だけ）

1. **ffmpegをインストール**
   - https://ffmpeg.org/download.html からダウンロード
   - またはコマンドプロンプトで: `winget install ffmpeg`

2. **Pythonライブラリをインストール**
   ```
   pip install pillow tqdm
   ```

---

## 使い方（毎回）

### 方法1: バッチファイルをダブルクリック（かんたん）
```
ツクヨミ_横型.bat     → ツクヨミシリーズの1時間動画
アマテラス_横型.bat   → アマテラスシリーズの1時間動画
スサノオ_横型.bat     → スサノオシリーズの1時間動画
叢雲の導き_横型.bat   → 叢雲の導きシリーズの動画
Shorts用_縦型.bat     → シリーズを入力してShorts用縦型を作成
```

### 方法2: コマンドプロンプトで実行
```
python make_video.py --series ツクヨミ
python make_video.py --series アマテラス --format shorts
```

---

## 出力先
```
D:\FIRE\SNS\SUNO\youtubu用\星詠み Lofi\output\
  ├── ツクヨミ_long.mp4
  ├── アマテラス_long.mp4
  ├── アマテラス_shorts.mp4
  └── ...
```

---

## 困ったとき
- `ffmpeg が見つかりません` → ffmpegのインストールを確認
- 画像が見つからないエラー → `make_video.py` の `IMAGE_DIR` のパスを確認
- 途中で止まる → 一度に処理する曲数が多い場合は曲を減らして試す

