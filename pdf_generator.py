"""PDF generation for 星詠みChronicle using reportlab."""
import os
import math
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fortune_data import TYPES, get_navigator_message

# ── Font setup ──────────────────────────────────────────────────────────
FONT_PATHS = [
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
]
FONT_BOLD_PATHS = [
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
]

_FONT_REGISTERED = False
FONT_NAME       = "IPAGothic"
FONT_BOLD_NAME  = "IPAGothicBold"


def _register_fonts():
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    for path in FONT_PATHS:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(FONT_NAME, path))
            break
    for path in FONT_BOLD_PATHS:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, path))
            break
    _FONT_REGISTERED = True


# ── Color palette ────────────────────────────────────────────────────────
C_BG        = HexColor("#0a0a1e")   # deep navy
C_BG2       = HexColor("#0f0f2d")   # slightly lighter navy
C_GOLD      = HexColor("#d4a843")   # antique gold
C_GOLD2     = HexColor("#f0c040")   # bright gold
C_WHITE     = HexColor("#f0eee8")   # warm white
C_SILVER    = HexColor("#c0bebe")   # silver
C_ACCENT    = HexColor("#7b5ea7")   # deep purple accent
C_ACCENT2   = HexColor("#4a3080")   # darker purple
C_DIM       = HexColor("#888888")   # dim gray

W, H = A4   # 595.28 x 841.89 pt


# ── Drawing helpers ──────────────────────────────────────────────────────

def _bg(c: canvas.Canvas):
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def _gold_border(c: canvas.Canvas, margin=18, inset=8):
    # Outer border
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(1.5)
    c.rect(margin, margin, W - 2*margin, H - 2*margin, fill=0, stroke=1)
    # Inner border
    c.setStrokeColor(C_GOLD2)
    c.setLineWidth(0.5)
    c.rect(margin + inset, margin + inset, W - 2*(margin+inset), H - 2*(margin+inset), fill=0, stroke=1)


def _star(c: canvas.Canvas, cx, cy, r, points=5, color=None):
    color = color or C_GOLD
    c.setFillColor(color)
    c.setStrokeColor(color)
    path = c.beginPath()
    for i in range(points * 2):
        angle = math.pi / 2 + i * math.pi / points
        radius = r if i % 2 == 0 else r * 0.4
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def _moon(c: canvas.Canvas, cx, cy, r, color=None):
    color = color or C_GOLD
    c.setFillColor(color)
    # Full circle
    c.circle(cx, cy, r, fill=1, stroke=0)
    # Cover with bg circle offset
    c.setFillColor(C_BG)
    c.circle(cx + r * 0.5, cy, r * 0.85, fill=1, stroke=0)


def _scatter_stars(c: canvas.Canvas, count=40, seed=42):
    import random
    rng = random.Random(seed)
    for _ in range(count):
        x = rng.uniform(30, W - 30)
        y = rng.uniform(30, H - 30)
        r = rng.uniform(1, 3)
        alpha = rng.uniform(0.3, 1.0)
        col = HexColor("#d4a843") if rng.random() > 0.5 else HexColor("#c0bebe")
        c.setFillColor(col)
        c.setFillAlpha(alpha)
        c.circle(x, y, r, fill=1, stroke=0)
    c.setFillAlpha(1.0)


def _text(c: canvas.Canvas, x, y, text, font=FONT_NAME, size=12, color=None, align="left"):
    color = color or C_WHITE
    c.setFont(font, size)
    c.setFillColor(color)
    if align == "center":
        c.drawCentredString(x, y, text)
    elif align == "right":
        c.drawRightString(x, y, text)
    else:
        c.drawString(x, y, text)


def _divider(c: canvas.Canvas, y, margin=40):
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.5)
    c.line(margin, y, W - margin, y)
    # Diamond ornaments
    for dx in [margin - 6, W - margin + 6]:
        _star(c, dx, y, 4, 4, C_GOLD)


def _section_box(c: canvas.Canvas, x, y, w, h, title=""):
    c.setFillColor(C_ACCENT2)
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=1)
    if title:
        c.setFillColor(C_GOLD)
        c.rect(x + 10, y + h - 14, len(title) * 14 + 10, 20, fill=1, stroke=0)
        _text(c, x + 15, y + h - 10, title, FONT_BOLD_NAME, 11, C_BG)


def _score_bar(c: canvas.Canvas, x, y, score: int, label: str, width=200):
    bar_h = 14
    # Label
    _text(c, x, y + bar_h - 2, label, FONT_BOLD_NAME, 11, C_GOLD)
    bar_x = x + 80
    # Background bar
    c.setFillColor(HexColor("#1a1a3e"))
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.5)
    c.roundRect(bar_x, y, width, bar_h, 4, fill=1, stroke=1)
    # Filled portion
    fill_w = width * score / 100
    grad_color = (
        HexColor("#8B0000") if score < 50 else
        HexColor("#8B6914") if score < 70 else
        HexColor("#d4a843") if score < 85 else
        HexColor("#f0c040")
    )
    c.setFillColor(grad_color)
    c.setStrokeColor(grad_color)
    c.roundRect(bar_x, y, fill_w, bar_h, 4, fill=1, stroke=0)
    # Score text
    _text(c, bar_x + width + 10, y + bar_h - 3, f"{score}点", FONT_BOLD_NAME, 12, C_GOLD2)


def _wrap_text(c: canvas.Canvas, x, y, text, font, size, color, max_width, line_height):
    """Simple word wrap for Japanese text (wraps by character count)."""
    c.setFont(font, size)
    c.setFillColor(color)
    chars_per_line = int(max_width / (size * 0.9))
    lines = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        while len(para) > chars_per_line:
            lines.append(para[:chars_per_line])
            para = para[chars_per_line:]
        lines.append(para)

    current_y = y
    for line in lines:
        c.drawString(x, current_y, line)
        current_y -= line_height
    return current_y


def _type_symbol(c: canvas.Canvas, cx, cy, type_id: int):
    """Draw a decorative symbol for the 12 type."""
    symbols = {
        1: ("炎", C_GOLD2),  2: ("海", HexColor("#4488cc")),
        3: ("雷", HexColor("#cccc44")), 4: ("森", HexColor("#44aa44")),
        5: ("月", HexColor("#ccaabb")), 6: ("陽", HexColor("#ffcc44")),
        7: ("岳", HexColor("#aa8866")), 8: ("嵐", HexColor("#88aacc")),
        9: ("花", HexColor("#ffaacc")), 10: ("氷", HexColor("#88ccee")),
        11: ("地", HexColor("#aa6622")), 12: ("星", HexColor("#aaaaff")),
    }
    char, col = symbols.get(type_id, ("？", C_GOLD))
    # Outer glow circle
    c.setFillColor(HexColor("#1a1a3e"))
    c.setStrokeColor(col)
    c.setLineWidth(2)
    c.circle(cx, cy, 55, fill=1, stroke=1)
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.8)
    c.circle(cx, cy, 62, fill=0, stroke=1)

    # Decorative stars around circle
    for i in range(8):
        angle = i * math.pi / 4
        sx = cx + 72 * math.cos(angle)
        sy = cy + 72 * math.sin(angle)
        _star(c, sx, sy, 4, 5, C_GOLD if i % 2 == 0 else C_SILVER)

    # Main character
    c.setFont(FONT_BOLD_NAME, 52)
    c.setFillColor(col)
    c.drawCentredString(cx, cy - 18, char)


# ── Pages ────────────────────────────────────────────────────────────────

def _page_cover(c: canvas.Canvas, data: dict):
    _bg(c)
    _scatter_stars(c, 60, seed=data["type_id"] * 13)
    _gold_border(c)

    # Top decorative moon
    _moon(c, W - 80, H - 70, 40, C_GOLD)
    _star(c, 80, H - 70, 18, 5, C_GOLD)
    _star(c, 60, H - 120, 10, 5, C_SILVER)
    _star(c, 110, H - 45, 7, 5, C_GOLD2)

    # Title logo
    _text(c, W/2, H - 90, "星 詠 み Chronicle", FONT_BOLD_NAME, 22, C_GOLD2, "center")
    _text(c, W/2, H - 110, "〜 Personal Fortune Reading 〜", FONT_NAME, 10, C_SILVER, "center")
    _divider(c, H - 125, margin=60)

    # Name
    name = data["name"]
    _text(c, W/2, H - 165, f"◈  {name}  様", FONT_BOLD_NAME, 20, C_GOLD2, "center")
    _text(c, W/2, H - 185, "個 人 鑑 定 書", FONT_BOLD_NAME, 14, C_SILVER, "center")

    # Type symbol (center)
    _type_symbol(c, W/2, H/2 + 30, data["type_id"])

    # Type name
    type_name = data["type"]["name"]
    _text(c, W/2, H/2 - 60, f"◆ {type_name} ◆", FONT_BOLD_NAME, 26, C_GOLD2, "center")
    _text(c, W/2, H/2 - 82, data["type"]["keyword"], FONT_NAME, 12, C_SILVER, "center")

    _divider(c, H/2 - 105, margin=60)

    # Birth & type info box
    bx, by = 80, H/2 - 175
    c.setFillColor(C_ACCENT2)
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.8)
    c.roundRect(bx, by, W - 160, 58, 8, fill=1, stroke=1)

    _text(c, W/2, by + 38, f"生年月日：{data['birth']}　血液型：{data['blood']['type']}型", FONT_NAME, 11, C_WHITE, "center")
    _text(c, W/2, by + 18, f"星座：{data['zodiac']['name']}　干支：{data['chinese']['name']}　数秘：{data['life_path']['number']}", FONT_NAME, 11, C_WHITE, "center")

    # Navigator
    _text(c, W/2, by - 25, f"ナビゲーター：{data['navigator']}", FONT_NAME, 11, C_GOLD, "center")

    # Bottom
    _divider(c, 75, margin=60)
    _text(c, W/2, 55, f"鑑定月：{data['month_str']}", FONT_NAME, 10, C_SILVER, "center")
    _star(c, 50, 50, 8, 5, C_GOLD)
    _star(c, W - 50, 50, 8, 5, C_GOLD)


def _page_four_axis(c: canvas.Canvas, data: dict):
    _bg(c)
    _scatter_stars(c, 30, seed=7)
    _gold_border(c)

    # Page title
    _star(c, W/2 - 95, H - 65, 8, 5, C_GOLD)
    _star(c, W/2 + 95, H - 65, 8, 5, C_GOLD)
    _text(c, W/2, H - 75, "◆ 四 軸 分 析 ◆", FONT_BOLD_NAME, 20, C_GOLD2, "center")
    _text(c, W/2, H - 95, "あなたを形作る4つの星の流れ", FONT_NAME, 10, C_SILVER, "center")
    _divider(c, H - 108)

    sections = [
        ("星　座", data["zodiac"]["symbol"] + " " + data["zodiac"]["name"],
         f'元素：{data["zodiac"]["element"]}　キーワード：{data["zodiac"]["keyword"]}',
         data["zodiac"]["desc"],
         HexColor("#ffd700")),
        ("干　支", data["chinese"]["name"],
         f'元素：{data["chinese"]["element"]}　キーワード：{data["chinese"]["keyword"]}',
         data["chinese"]["desc"],
         HexColor("#e8aa44")),
        ("数 秘 術", f'ライフパスナンバー　{data["life_path"]["number"]}',
         f'キーワード：{data["life_path"]["keyword"]}',
         data["life_path"]["desc"],
         HexColor("#cc88ff")),
        ("血 液 型", f'{data["blood"]["type"]}型',
         f'キーワード：{data["blood"]["keyword"]}',
         data["blood"]["desc"],
         HexColor("#ff8888")),
    ]

    box_h = 140
    gap   = 15
    start_y = H - 125

    for i, (title, main, sub, desc, accent) in enumerate(sections):
        y_top = start_y - i * (box_h + gap)
        bx, bw = 35, W - 70

        # Box background
        c.setFillColor(C_ACCENT2)
        c.setStrokeColor(accent)
        c.setLineWidth(1)
        c.roundRect(bx, y_top - box_h, bw, box_h, 8, fill=1, stroke=1)

        # Left accent bar
        c.setFillColor(accent)
        c.roundRect(bx, y_top - box_h, 5, box_h, 3, fill=1, stroke=0)

        # Title badge
        badge_w = len(title) * 13 + 14
        c.setFillColor(accent)
        c.roundRect(bx + 14, y_top - 14, badge_w, 22, 5, fill=1, stroke=0)
        _text(c, bx + 14 + badge_w/2, y_top - 9, title, FONT_BOLD_NAME, 11, C_BG, "center")

        # Main text
        _text(c, bx + 25, y_top - 38, main, FONT_BOLD_NAME, 17, C_WHITE)

        # Sub text
        _text(c, bx + 25, y_top - 60, sub, FONT_NAME, 10, C_GOLD)

        # Divider line
        c.setStrokeColor(accent)
        c.setLineWidth(0.4)
        c.line(bx + 15, y_top - 72, bx + bw - 15, y_top - 72)

        # Description (wrapped)
        chars = int((bw - 50) / 10)
        desc_lines = []
        tmp = desc
        while len(tmp) > chars:
            desc_lines.append(tmp[:chars])
            tmp = tmp[chars:]
        desc_lines.append(tmp)

        dy = y_top - 88
        for line in desc_lines:
            _text(c, bx + 25, dy, line, FONT_NAME, 10, C_SILVER)
            dy -= 15

    # Bottom decoration
    _divider(c, 45)
    _text(c, W/2, 28, "Page 1", FONT_NAME, 8, C_DIM, "center")


def _page_fortune(c: canvas.Canvas, data: dict):
    _bg(c)
    _scatter_stars(c, 25, seed=99)
    _gold_border(c)

    _star(c, W/2 - 85, H - 65, 8, 5, C_GOLD)
    _star(c, W/2 + 85, H - 65, 8, 5, C_GOLD)
    _text(c, W/2, H - 75, "◆ 今 月 の 運 勢 ◆", FONT_BOLD_NAME, 20, C_GOLD2, "center")
    _text(c, W/2, H - 95, f"〜 {data['month_str']} 〜", FONT_NAME, 11, C_SILVER, "center")
    _divider(c, H - 108)

    categories = ["総合", "恋愛", "金運", "仕事"]
    cat_labels  = {"総合": "総合運", "恋愛": "恋愛運", "金運": "金　運", "仕事": "仕事運"}
    cat_icons   = {"総合": "✦", "恋愛": "❤", "金運": "◈", "仕事": "★"}

    start_y = H - 130
    block_h = 148
    gap     = 12

    for i, cat in enumerate(categories):
        score = data["scores"][cat]
        msg   = data["type"]["fortune_messages"][cat]
        y_top = start_y - i * (block_h + gap)

        bx, bw = 35, W - 70
        # Block bg
        c.setFillColor(C_BG2)
        c.setStrokeColor(C_GOLD)
        c.setLineWidth(0.8)
        c.roundRect(bx, y_top - block_h, bw, block_h, 8, fill=1, stroke=1)

        # Category header
        label = cat_labels[cat]
        icon  = cat_icons[cat]
        _text(c, bx + 20, y_top - 22, f"{icon}  {label}", FONT_BOLD_NAME, 14, C_GOLD2)

        # Score bar
        _score_bar(c, bx + 20, y_top - 48, score, "運勢スコア", width=260)

        # Rank stars
        star_count = min(5, max(1, int(score / 20)))
        star_x = bx + 360
        for s in range(5):
            col = C_GOLD2 if s < star_count else C_DIM
            _star(c, star_x + s * 18, y_top - 42, 7, 5, col)

        # Divider
        c.setStrokeColor(C_ACCENT)
        c.setLineWidth(0.3)
        c.line(bx + 15, y_top - 60, bx + bw - 15, y_top - 60)

        # Message (wrapped)
        chars = int((bw - 50) / 10)
        lines = []
        tmp = msg
        while len(tmp) > chars:
            lines.append(tmp[:chars])
            tmp = tmp[chars:]
        lines.append(tmp)

        dy = y_top - 78
        for line in lines:
            _text(c, bx + 20, dy, line, FONT_NAME, 10, C_WHITE)
            dy -= 15

    _divider(c, 45)
    _text(c, W/2, 28, "Page 2", FONT_NAME, 8, C_DIM, "center")


def _page_navigator(c: canvas.Canvas, data: dict):
    _bg(c)
    _scatter_stars(c, 35, seed=55)
    _gold_border(c)

    nav  = data["navigator"]
    nav_data = get_navigator_message(nav, data["type_id"], data["name"])

    _star(c, 60, H - 65, 12, 5, C_GOLD)
    _star(c, W - 60, H - 65, 12, 5, C_GOLD)
    _text(c, W/2, H - 68, f"◆ ナビゲーター {nav} より ◆", FONT_BOLD_NAME, 18, C_GOLD2, "center")
    _text(c, W/2, H - 90, nav_data["header"], FONT_NAME, 11, C_SILVER, "center")
    _divider(c, H - 103)

    # Navigator portrait box
    nav_colors = {
        "叢雲": (HexColor("#1a1a4e"), HexColor("#8888ff")),
        "ノヴァ": (HexColor("#2a1a1a"), HexColor("#ff6644")),
        "フレイヤ": (HexColor("#1a2a1a"), HexColor("#66aa66")),
        "グレイス": (HexColor("#1e1e2e"), HexColor("#aaaacc")),
    }
    nav_bg, nav_accent = nav_colors.get(nav, (C_ACCENT2, C_GOLD))
    nav_emojis = {"叢雲": "🌙", "ノヴァ": "⭐", "フレイヤ": "🐱", "グレイス": "❄"}

    # Portrait circle
    c.setFillColor(nav_bg)
    c.setStrokeColor(nav_accent)
    c.setLineWidth(2)
    c.circle(W/2, H - 215, 65, fill=1, stroke=1)
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.8)
    c.circle(W/2, H - 215, 74, fill=0, stroke=1)

    # Navigator name large
    _text(c, W/2, H - 208, nav, FONT_BOLD_NAME, 28, nav_accent, "center")

    # Nav intro
    _text(c, W/2, H - 300, nav_data["intro"], FONT_NAME, 11, C_GOLD, "center")

    _divider(c, H - 315, margin=60)

    # Message box
    msg_y = H - 335
    msg_x = 50
    msg_w = W - 100
    msg_h = 300

    c.setFillColor(nav_bg)
    c.setStrokeColor(nav_accent)
    c.setLineWidth(1)
    c.roundRect(msg_x, msg_y - msg_h, msg_w, msg_h, 10, fill=1, stroke=1)

    # Quote marks
    c.setFont(FONT_BOLD_NAME, 60)
    c.setFillColor(nav_accent)
    c.setFillAlpha(0.3)
    c.drawString(msg_x + 10, msg_y - 30, "「")
    c.drawRightString(msg_x + msg_w - 10, msg_y - msg_h + 10, "」")
    c.setFillAlpha(1.0)

    # Message text
    msg   = nav_data["message"]
    chars = int((msg_w - 60) / 11)
    lines = []
    tmp   = msg
    for para in tmp.split("。"):
        if not para:
            continue
        para += "。"
        while len(para) > chars:
            lines.append(para[:chars])
            para = para[chars:]
        lines.append(para)
        lines.append("")

    dy = msg_y - 48
    for line in lines:
        if dy < msg_y - msg_h + 25:
            break
        _text(c, msg_x + 25, dy, line, FONT_NAME, 11, C_WHITE)
        dy -= 20

    _divider(c, 45)
    _text(c, W/2, 28, "Page 3", FONT_NAME, 8, C_DIM, "center")


def _page_lucky(c: canvas.Canvas, data: dict):
    _bg(c)
    _scatter_stars(c, 30, seed=77)
    _gold_border(c)

    type_data = data["type"]

    _star(c, W/2 - 110, H - 65, 8, 5, C_GOLD)
    _star(c, W/2 + 110, H - 65, 8, 5, C_GOLD)
    _text(c, W/2, H - 75, "◆ 今 月 の 開 運 情 報 ◆", FONT_BOLD_NAME, 20, C_GOLD2, "center")
    _text(c, W/2, H - 95, "あなたに幸運をもたらす星からの贈り物", FONT_NAME, 10, C_SILVER, "center")
    _divider(c, H - 108)

    # Lucky Items
    sec_y = H - 135
    _section_box(c, 35, sec_y - 110, W - 70, 120, "✦ ラッキーアイテム")
    items = type_data["lucky_items"]
    for j, item in enumerate(items):
        ix = 65 + (j % 2) * (W/2 - 50)
        iy = sec_y - 48 - (j // 2) * 30
        _star(c, ix - 15, iy + 4, 5, 5, C_GOLD2)
        _text(c, ix, iy, item, FONT_NAME, 11, C_WHITE)

    # Lucky Colors
    col_y = sec_y - 130
    _section_box(c, 35, col_y - 110, W - 70, 120, "◈ ラッキーカラー")
    colors = type_data["lucky_colors"]
    swatch_w = (W - 120) / len(colors)
    for j, (cname, chex) in enumerate(colors):
        sw_x = 50 + j * swatch_w
        sw_y = col_y - 95
        c.setFillColor(HexColor(chex))
        c.setStrokeColor(C_GOLD)
        c.setLineWidth(0.5)
        c.roundRect(sw_x, sw_y, swatch_w - 15, 35, 5, fill=1, stroke=1)
        _text(c, sw_x + (swatch_w-15)/2, sw_y - 16, cname, FONT_NAME, 10, C_WHITE, "center")

    # Advice
    adv_y = col_y - 140
    _section_box(c, 35, adv_y - 180, W - 70, 185, "★ 今月のアドバイス")

    # Generate advice from type traits
    traits = type_data["traits"]
    advice_lines = [
        f"◉ {data['month_str']}、{data['type']['name']}であるあなたへ",
        "",
        f"あなたの本質は「{type_data['keyword']}」にあります。",
        type_data["desc"][:40] + "……",
        "",
    ] + [f"◆ {t}" for t in traits]

    dy = adv_y - 40
    for line in advice_lines:
        if not line:
            dy -= 6
            continue
        color = C_GOLD if line.startswith("◉") else C_WHITE if line.startswith("◆") else C_SILVER
        size  = 12 if line.startswith("◉") else 10
        _text(c, 55, dy, line, FONT_NAME, size, color)
        dy -= 18

    _divider(c, 45)
    _text(c, W/2, 28, "Page 4", FONT_NAME, 8, C_DIM, "center")


def _page_back(c: canvas.Canvas, data: dict):
    _bg(c)
    _scatter_stars(c, 80, seed=1234)
    _gold_border(c)

    # Large decorative moon
    _moon(c, W/2, H - 150, 80, C_GOLD)

    # Decorative stars
    for angle_deg, r_dist, size in [(30, 140, 15), (150, 140, 12), (90, 160, 10),
                                     (210, 120, 8), (330, 120, 8), (0, 180, 6)]:
        angle = math.radians(angle_deg)
        sx = W/2 + r_dist * math.cos(angle)
        sy = (H - 150) + r_dist * math.sin(angle)
        _star(c, sx, sy, size, 5, C_GOLD)

    # Logo
    _text(c, W/2, H/2 + 40, "星 詠 み Chronicle", FONT_BOLD_NAME, 30, C_GOLD2, "center")
    _text(c, W/2, H/2 + 10, "Hoshiyomi Chronicle", FONT_NAME, 14, C_SILVER, "center")
    _divider(c, H/2 - 10, margin=80)

    _text(c, W/2, H/2 - 38, "〜 星の導きに従い、あなたの道を歩んでください 〜", FONT_NAME, 10, C_SILVER, "center")

    # URL box
    url_y = H/2 - 80
    c.setFillColor(C_ACCENT2)
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.8)
    c.roundRect(W/2 - 150, url_y - 20, 300, 35, 8, fill=1, stroke=1)
    _text(c, W/2, url_y - 6, "https://hoshiyomi-chronicle.booth.pm", FONT_NAME, 11, C_GOLD2, "center")

    _text(c, W/2, url_y - 45, "© 星詠みChronicle  All Rights Reserved", FONT_NAME, 9, C_DIM, "center")

    # Bottom corner stars
    for sx, sy in [(45, 45), (W - 45, 45), (45, H - 45), (W - 45, H - 45)]:
        _star(c, sx, sy, 10, 5, C_GOLD)


# ── Main entrypoint ──────────────────────────────────────────────────────

def generate_pdf(data: dict, output_path: str = None) -> bytes:
    _register_fonts()

    buf = BytesIO()
    target = output_path or buf

    c = canvas.Canvas(str(target) if output_path else buf, pagesize=A4)
    c.setTitle(f"星詠みChronicle 個人鑑定書 - {data['name']}様")
    c.setAuthor("星詠みChronicle")
    c.setSubject(f"{data['type']['name']} 個人鑑定")

    # Cover
    _page_cover(c, data)
    c.showPage()

    # Page 1: 4軸分析
    _page_four_axis(c, data)
    c.showPage()

    # Page 2: 運勢スコア
    _page_fortune(c, data)
    c.showPage()

    # Page 3: ナビゲーターメッセージ
    _page_navigator(c, data)
    c.showPage()

    # Page 4: ラッキー情報
    _page_lucky(c, data)
    c.showPage()

    # Back cover
    _page_back(c, data)
    c.showPage()

    c.save()

    if output_path:
        return None
    return buf.getvalue()
