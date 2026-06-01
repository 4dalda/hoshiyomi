"""
星詠みLofi 動画自動生成スクリプト
====================================
使い方:
  python make_video.py --series ツクヨミ
  python make_video.py --series アマテラス --format shorts
  python make_video.py --series 叢雲の導き --format long

必要なもの:
  - ffmpeg (PATH が通っていること)
  - Python 3.8+
  - pip install pillow tqdm
"""

import argparse
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

# ============================================================
# パス設定（ここだけ変更すればOK）
# ============================================================
BASE_DIR   = Path(r"D:\FIRE\SNS\SUNO\youtubu用\星詠み Lofi")
MUSIC_DIR  = BASE_DIR / "素材楽曲"
IMAGE_DIR  = BASE_DIR / "素材静止画"
OUTPUT_DIR = BASE_DIR / "output"

# シリーズ名 → 音楽フォルダ・画像フォルダ のマッピング
SERIES_MAP = {
    "月":         {"music": "00月シリーズ_神秘・静寂",    "image": "ツクヨミ"},
    "星":         {"music": "01星シリーズ_幻想・宇宙",     "image": "アマテラス"},
    "祭":         {"music": "02祭シリーズ",               "image": "祭"},
    "アマテラス": {"music": "04アマテラス/00アマテラス",   "image": "アマテラス"},
    "ツクヨミ":   {"music": "05ツクヨミ/00ツクヨミ",       "image": "ツクヨミ"},
    "スサノオ":   {"music": "06スサノオ/00スサノオ",       "image": "スサノオ"},
    "叢雲の導き": {"music": "叢雲の導き",                  "image": "叢雲"},
}

# 動画フォーマット
FORMATS = {
    "long":   {"width": 1920, "height": 1080, "label": "横型(1時間)"},
    "shorts": {"width": 1080, "height": 1920, "label": "縦型Shorts"},
}

# 目標動画時間（秒）。3600 = 1時間
TARGET_DURATION_SEC = 3600

# 1枚の画像を表示する秒数
IMAGE_DURATION_SEC = 30

# ============================================================

def find_files(folder: Path, exts: list) -> list:
    files = []
    for ext in exts:
        files.extend(sorted(folder.glob(f"**/*{ext}")))
    return files


def get_audio_duration(path: Path) -> float:
    """ffprobeで音声の長さを取得"""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def make_video(series: str, fmt: str = "long"):
    if series not in SERIES_MAP:
        print(f"エラー: シリーズ '{series}' が見つかりません")
        print(f"使えるシリーズ: {', '.join(SERIES_MAP.keys())}")
        sys.exit(1)

    mapping   = SERIES_MAP[series]
    music_dir = MUSIC_DIR / mapping["music"]
    image_dir = IMAGE_DIR / mapping["image"]
    fmt_info  = FORMATS[fmt]

    print(f"\n🎵 シリーズ: {series} [{fmt_info['label']}]")
    print(f"   音楽フォルダ: {music_dir}")
    print(f"   画像フォルダ: {image_dir}")

    # ファイル収集
    audio_files = find_files(music_dir, [".wav", ".mp3", ".flac", ".m4a"])
    image_files = find_files(image_dir, [".png", ".jpg", ".jpeg", ".webp"])

    if not audio_files:
        print(f"エラー: 音楽ファイルが見つかりません → {music_dir}")
        sys.exit(1)
    if not image_files:
        print(f"エラー: 画像ファイルが見つかりません → {image_dir}")
        sys.exit(1)

    print(f"   音楽: {len(audio_files)}曲 / 画像: {len(image_files)}枚")

    # Shortsは30秒、longは1時間
    import math
    if fmt == "shorts":
        total_audio_sec = 28
        audio_files = [audio_files[0]]  # 最初の1曲だけ使用
    else:
        print("\n⏱  音声の長さを確認中...")
        single_loop_sec = sum(get_audio_duration(f) for f in audio_files)
        print(f"   1ループ: {single_loop_sec/60:.1f}分")
        loop_count = math.ceil(TARGET_DURATION_SEC / single_loop_sec)
        total_audio_sec = TARGET_DURATION_SEC
        audio_files = list(audio_files) * loop_count
        print(f"   {loop_count}回ループ → 合計約{total_audio_sec/60:.0f}分")

    # 出力先
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_series = series.replace("/", "_").replace("\\", "_")
    output_path = OUTPUT_DIR / f"{safe_series}_{fmt}.mp4"

    W, H = fmt_info["width"], fmt_info["height"]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # ── Step 1: 音楽を結合 ──────────────────────────────────
        print("\n🎵 音楽を結合中...")
        concat_txt = tmpdir / "audio_list.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for af in audio_files:
                f.write(f"file '{af.as_posix()}'\n")

        merged_audio = tmpdir / "merged_audio.wav"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c", "copy", str(merged_audio)
        ], check=True, capture_output=True)

        # ── Step 2: 画像スライドショー動画を生成 ─────────────────
        print("🖼  スライドショーを生成中（時間がかかります）...")

        # 画像を必要枚数ループさせる
        n_images_needed = max(1, int(total_audio_sec / IMAGE_DURATION_SEC) + 1)
        image_cycle = [image_files[i % len(image_files)] for i in range(n_images_needed)]

        # filter_complexでクロスフェード
        filter_parts = []
        inputs = []
        for i, img in enumerate(image_cycle):
            inputs += ["-loop", "1", "-t", str(IMAGE_DURATION_SEC), "-i", str(img)]

        # 画像をスケール＆パディングして統一サイズに
        scale_filter = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"

        # 各画像クリップをスケール
        for i in range(len(image_cycle)):
            filter_parts.append(f"[{i}:v]{scale_filter},setsar=1[v{i}]")

        # クロスフェードでつなぐ（xfadeフィルタ）
        FADE_DUR = 1.5  # フェード時間（秒）
        prev = "v0"
        for i in range(1, len(image_cycle)):
            offset = IMAGE_DURATION_SEC * i - FADE_DUR * i
            next_v = f"xf{i}"
            filter_parts.append(
                f"[{prev}][v{i}]xfade=transition=fade:duration={FADE_DUR}:offset={offset}[{next_v}]"
            )
            prev = next_v

        filter_complex = ";".join(filter_parts)
        slideshow_path = tmpdir / "slideshow.mp4"

        cmd = ["ffmpeg", "-y"]
        cmd += inputs
        cmd += [
            "-filter_complex", filter_complex,
            "-map", f"[{prev}]",
            "-t", str(total_audio_sec),
            "-c:v", "libx264", "-preset", "fast", "-crf", "28",
            "-pix_fmt", "yuv420p",
            str(slideshow_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # ── Step 3: 動画と音楽を合成 ─────────────────────────────
        print("🎬 動画と音楽を合成中...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(slideshow_path),
            "-i", str(merged_audio),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_path)
        ], check=True, capture_output=True)

    print(f"\n✅ 完成！")
    print(f"   出力先: {output_path}")
    print(f"   ファイルサイズ: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"\n📺 YouTubeにアップロードする準備ができました！")


def main():
    parser = argparse.ArgumentParser(description="星詠みLofi 動画自動生成")
    parser.add_argument("--series", required=True,
                        help=f"シリーズ名: {', '.join(SERIES_MAP.keys())}")
    parser.add_argument("--format", default="long", choices=["long", "shorts"],
                        help="long=横型1時間, shorts=縦型")
    args = parser.parse_args()
    make_video(args.series, args.format)


if __name__ == "__main__":
    main()
