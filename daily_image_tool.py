"""
星詠みChronicle 毎日ありがたい画像ツール
- 画像にテキストを合成
- 日付でファイル整理
- 月末にZIPまとめ
"""

import os
import zipfile
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillowをインストールしてください: pip install Pillow")
    exit(1)

# フォルダ設定
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "daily_images"
OUTPUT_DIR.mkdir(exist_ok=True)

# 曜日別テーマ
WEEKLY_THEMES = {
    0: "龍神",    # 月
    1: "星空・宇宙",  # 火
    2: "神社・聖地",  # 水
    3: "天使・光",   # 木
    4: "花・自然",   # 金
    5: "星座・月",   # 土
    6: "感謝・言霊",  # 日
}

# 曜日別メッセージ
WEEKLY_MESSAGES = {
    0: "龍神があなたの道を照らしています",
    1: "星があなたを見守っています",
    2: "聖地からの祝福があなたに届きます",
    3: "天使があなたを守っています",
    4: "自然の恵みがあなたに注がれています",
    5: "月の光があなたを包んでいます",
    6: "今日もありがとうございます",
}


def add_text_to_image(image_path: str, output_path: str, message: str = None):
    """画像にテキストを合成して保存する"""
    today = datetime.now()
    weekday = today.weekday()

    if message is None:
        message = WEEKLY_MESSAGES[weekday]

    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 下部に半透明の黒帯
    band_height = int(height * 0.2)
    draw.rectangle(
        [(0, height - band_height), (width, height)],
        fill=(0, 0, 0, 160)
    )

    # フォント設定（日本語対応フォントを探す）
    font_size = max(24, width // 20)
    font = None
    font_candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        str(BASE_DIR / "fonts" / "NotoSansJP-Regular.ttf"),
    ]
    for f in font_candidates:
        if Path(f).exists():
            try:
                font = ImageFont.truetype(f, font_size)
                break
            except Exception:
                continue
    if font is None:
        font = ImageFont.load_default()

    # テキスト描画（中央揃え）
    bbox = draw.textbbox((0, 0), message, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (width - text_w) // 2
    text_y = height - band_height + (band_height - font_size) // 2

    # 影
    draw.text((text_x + 2, text_y + 2), message, font=font, fill=(0, 0, 0, 200))
    # 本文（ゴールド）
    draw.text((text_x, text_y), message, font=font, fill=(255, 215, 0, 255))

    # 右下に星詠みChronicle
    credit = "✨ 星詠みChronicle"
    credit_size = max(14, font_size // 2)
    try:
        credit_font = ImageFont.truetype(font_candidates[0], credit_size) if Path(font_candidates[0]).exists() else font
    except Exception:
        credit_font = font
    draw.text((width - 200, height - 30), credit, font=credit_font, fill=(255, 215, 0, 180))

    # 合成
    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, quality=95)
    print(f"✅ 保存しました: {output_path}")


def organize_by_date(image_path: str):
    """画像を日付フォルダに整理して保存"""
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    weekday = today.weekday()
    theme = WEEKLY_THEMES[weekday]

    date_dir = OUTPUT_DIR / today.strftime("%Y-%m")
    date_dir.mkdir(exist_ok=True)

    filename = f"{date_str}_{theme}.jpg"
    output_path = str(date_dir / filename)

    add_text_to_image(image_path, output_path)
    return output_path


def create_monthly_zip(year_month: str = None):
    """月ごとのZIPファイルを作成（例: 2026-09）"""
    if year_month is None:
        year_month = datetime.now().strftime("%Y-%m")

    month_dir = OUTPUT_DIR / year_month
    if not month_dir.exists():
        print(f"❌ フォルダが見つかりません: {month_dir}")
        return

    zip_path = OUTPUT_DIR / f"星詠みChronicle_神聖画像集_{year_month}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for img_file in sorted(month_dir.glob("*.jpg")):
            zf.write(img_file, img_file.name)
            print(f"  追加: {img_file.name}")

    print(f"\n✅ ZIP作成完了: {zip_path}")
    print(f"   ファイル数: {len(list(month_dir.glob('*.jpg')))}枚")
    return str(zip_path)


def show_today_info():
    """今日のテーマとメッセージを表示"""
    today = datetime.now()
    weekday = today.weekday()
    weekday_names = ["月", "火", "水", "木", "金", "土", "日"]
    print(f"\n📅 今日: {today.strftime('%Y年%m月%d日')}（{weekday_names[weekday]}曜日）")
    print(f"🎨 テーマ: {WEEKLY_THEMES[weekday]}")
    print(f"💬 メッセージ: {WEEKLY_MESSAGES[weekday]}")
    print()


if __name__ == "__main__":
    import sys

    show_today_info()

    if len(sys.argv) < 2:
        print("使い方:")
        print("  python daily_image_tool.py <画像ファイルパス>")
        print("  python daily_image_tool.py zip [年月 例:2026-09]")
        print()
        print("例:")
        print("  python daily_image_tool.py 龍神画像.jpg")
        print("  python daily_image_tool.py zip 2026-09")
    elif sys.argv[1] == "zip":
        year_month = sys.argv[2] if len(sys.argv) > 2 else None
        create_monthly_zip(year_month)
    else:
        image_path = sys.argv[1]
        if not Path(image_path).exists():
            print(f"❌ ファイルが見つかりません: {image_path}")
        else:
            organize_by_date(image_path)
