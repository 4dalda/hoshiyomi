"""
叢雲 画像自動生成スクリプト（OpenAI DALL-E 3使用）
=====================================================
使い方:
  python 画像自動生成.py --character 叢雲 --count 5

必要なもの:
  pip install openai pillow requests
  環境変数 OPENAI_API_KEY を設定すること
"""

import argparse
import os
import time
import requests
from pathlib import Path
from openai import OpenAI

# ============================================================
# 設定
# ============================================================
OUTPUT_BASE = Path(r"D:\FIRE\SNS\SUNO\youtubu用\星詠み Lofi\素材静止画")

# キャラクター別プロンプト
CHARACTER_PROMPTS = {
    "叢雲": [
        "A beautiful nekomimi girl, calico cat ears and fluffy calico tail, wearing an elegant white kimono with gold floral embroidery and black obi sash, white flower hairpin, standing before a large stone torii gate under a full moon, ancient Japanese shrine, stone lanterns glowing softly, silver moonlight, cherry blossom petals falling, mystical atmosphere, deep blue and silver night sky, shooting stars visible, cinematic anime illustration, highly detailed, ethereal lighting",
        "Murakumo, a calico nekomimi girl in white and gold kimono, sitting seiza on a wooden shrine veranda, looking up at a breathtaking star-filled sky, the Milky Way stretching overhead, a small glowing orb of light floating near her hand, ancient scrolls and star charts spread around her, soft golden candlelight from paper lanterns, serene and mysterious mood, dark blue night with silver star reflections on a still pond below, cinematic anime art style, ultra detailed",
        "Calico cat girl with white kimono and gold obi, standing on ocean rocks at night, dramatic crashing waves with bioluminescent blue glow, a red torii gate rising from the sea in the background, full moon creating a silver path on the water, her calico tail curled around her feet, white flowers in her dark and gold hair, dramatic cinematic lighting, Japanese mythological atmosphere, anime illustration, highly detailed, moonlit ocean",
        "Elegant calico nekomimi shrine maiden in white and gold kimono, walking down a long stone shrine pathway, enormous ancient cherry blossom trees on both sides in full bloom, pink petals swirling in warm golden sunset light, stone lanterns lining the path, warm orange and pink sky, her expression gentle and calm, soft bokeh background, cinematic anime, detailed fabric texture",
        "Calico cat girl in white kimono, lying on a grassy hilltop looking up at the night sky, surrounded by glowing fireflies, the Milky Way galaxy stretching dramatically above, ancient temple silhouette in the far background, soft purple and blue cosmic colors, golden firefly light reflecting on her kimono, peaceful and dreamlike, cinematic anime illustration, extremely detailed, cosmic fantasy",
    ],
    "アマテラス": [
        "A radiant goddess with sun motifs, golden kimono, standing at the gates of heaven, Japanese deity, cinematic anime, ethereal golden light",
    ],
    "ツクヨミ": [
        "A serene moon goddess, silver and white kimono, midnight blue atmosphere, Japanese lunar deity, cinematic anime, moonlight",
    ],
    "スサノオ": [
        "A powerful storm god, dark blue and purple kimono, dramatic thunder and lightning, Japanese deity, cinematic anime, epic atmosphere",
    ],
}

# ============================================================

def generate_images(character: str, count: int):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("エラー: OPENAI_API_KEY 環境変数が設定されていません")
        print("設定方法: set OPENAI_API_KEY=sk-xxxxx")
        return

    if character not in CHARACTER_PROMPTS:
        print(f"エラー: キャラクター '{character}' が見つかりません")
        print(f"使えるキャラクター: {', '.join(CHARACTER_PROMPTS.keys())}")
        return

    client = OpenAI(api_key=api_key)
    output_dir = OUTPUT_BASE / character
    output_dir.mkdir(parents=True, exist_ok=True)

    prompts = CHARACTER_PROMPTS[character]
    count = min(count, len(prompts))

    print(f"\n🎨 {character} の画像を {count} 枚生成します...")
    print(f"   保存先: {output_dir}\n")

    for i in range(count):
        prompt = prompts[i]
        print(f"  [{i+1}/{count}] 生成中...")

        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",   # 16:9 横型
                quality="hd",
                n=1,
            )
            image_url = response.data[0].url

            # ダウンロード
            img_data = requests.get(image_url).content
            filename = output_dir / f"{character}_{i+1:02d}.png"
            with open(filename, "wb") as f:
                f.write(img_data)

            print(f"  ✅ 保存: {filename.name}")
            time.sleep(3)   # レート制限対策

        except Exception as e:
            print(f"  ❌ エラー: {e}")

    print(f"\n✅ 完了！ {output_dir} を確認してください")


def main():
    parser = argparse.ArgumentParser(description="星詠み 画像自動生成 (DALL-E 3)")
    parser.add_argument("--character", default="叢雲",
                        help=f"キャラクター名: {', '.join(CHARACTER_PROMPTS.keys())}")
    parser.add_argument("--count", type=int, default=5, help="生成枚数（最大5）")
    args = parser.parse_args()
    generate_images(args.character, args.count)


if __name__ == "__main__":
    main()
