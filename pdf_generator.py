"""PDF generation v2 for 星詠みChronicle — improved design with image support."""
import os, math
from io import BytesIO
from reportlab.pdfgen import canvas as _Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth as SW
from fortune_data import TYPES, get_navigator_message

# ─── Image file mapping ───────────────────────────────────────────────────
_BASE   = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(_BASE, "static", "images")

TYPE_IMGS = {
     1: "01SD炎の龍.png",    2: "02SD深海の人魚.png",  3: "03SD雷の天使.png",
     4: "04SD森の精霊.png",   5: "05SD月の魔女.png",    6: "06SD太陽の勇者.png",
     7: "07SD山の巨人.png",   8: "08SD嵐の鷲.png",     9: "09SD花の女神.png",
    10: "10SD氷の龍.png",   11: "11SD大地の魔神.png", 12: "12SD星の賢者.png",
}
NAV_IMGS = {
    "叢雲":   "叢雲SD.png",
    "ノヴァ":  "ノヴァSD.png",
    "フレイヤ": "フレイアSD.png",
    "グレイス": "グレイスSD.png",
}
def _type_img_path(tid): return os.path.join(IMG_DIR, TYPE_IMGS.get(tid, ""))
def _nav_img_path(nav):  return os.path.join(IMG_DIR, NAV_IMGS.get(nav, ""))

# ─── Font registration ─────────────────────────────────────────────────────
FN   = "HoshiR"    # IPA Gothic  — UI labels, headers, scores
FNB  = "HoshiB"    # IPA PGothic — bold UI labels, badges
FNS  = "HoshiS"    # IPAex Mincho (明朝体) — narrative / body text
FNSL = "HoshiSL"   # FreeSerif — Latin decorative titles (Chronicle etc.)
_FONT_DONE = False

def _setup_fonts():
    global _FONT_DONE
    if _FONT_DONE:
        return
    for p in [
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    ]:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(FN, p))
            break
    for p in [
        "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    ]:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(FNB, p))
            break
    # IPAex Mincho — Japanese serif, traditional fortune-telling feel
    for p in [
        "/usr/share/fonts/opentype/ipaexfont-mincho/ipaexm.ttf",
        "/usr/share/fonts/truetype/fonts-japanese-mincho.ttf",
    ]:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(FNS, p))
            break
    else:
        pdfmetrics.registerFont(TTFont(FNS, "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))
    # FreeSerif — Latin glyphs for decorative ASCII title text
    for p in [
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]:
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(FNSL, p))
            break
    else:
        pdfmetrics.registerFont(TTFont(FNSL, "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))
    _FONT_DONE = True

# ─── Color palette ─────────────────────────────────────────────────────────
BG   = HexColor("#0a0a2e")   # deep navy (user specified)
BG2  = HexColor("#0f0f3a")
BG3  = HexColor("#141448")
PRP3 = HexColor("#1a1040")
PRP2 = HexColor("#3a2060")
PRP  = HexColor("#6a4ea8")
GLD  = HexColor("#c9a84c")   # main gold (user specified)
GLD2 = HexColor("#e8c060")
GLD3 = HexColor("#f5d878")
GLD_DARK = HexColor("#7a5d10")   # gold shadow for depth/bevel
GLD_LITE = HexColor("#fffac8")   # bright gold highlight/gloss
SLV  = HexColor("#c8c4bc")
WHT  = HexColor("#f0ece8")
DIM  = HexColor("#505070")

W, H = A4   # 595.28 × 841.89

# ─── Layout constants ──────────────────────────────────────────────────────
MG  = 22     # page margin
BDG = 7      # double-border inner gap
HDR_LINE = 785    # y of header separator line
FTR_LINE = 50     # y of footer separator line
CX1 = MG + BDG + 10   # content left x
CX2 = W - MG - BDG - 10  # content right x
CY1 = FTR_LINE + 10       # content bottom y
CY2 = HDR_LINE - 10       # content top y
CW  = CX2 - CX1           # content width (~528 pt)

# ─── Type accent colors ────────────────────────────────────────────────────
_TACC = {
     1: "#e85020",  2: "#3388cc",  3: "#d4c820",  4: "#44aa44",
     5: "#cc88bb",  6: "#ffcc22",  7: "#aa8855",  8: "#6699dd",
     9: "#ff99bb", 10: "#55ccee", 11: "#cc7733", 12: "#9999ff",
}
def TC(tid): return HexColor(_TACC.get(tid, "#c9a84c"))

# ─── Primitive drawing helpers ─────────────────────────────────────────────

def _star(c, cx, cy, r, pts=5, col=None):
    col = col or GLD
    c.setFillColor(col)
    path = c.beginPath()
    for i in range(pts * 2):
        angle = math.pi / 2 + i * math.pi / pts
        rad = r if i % 2 == 0 else r * 0.4
        x = cx + rad * math.cos(angle)
        y = cy + rad * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def _moon(c, cx, cy, r, col=None):
    col = col or GLD
    c.setFillColor(col)
    c.circle(cx, cy, r, fill=1, stroke=0)
    c.setFillColor(BG)
    c.circle(cx + r * 0.55, cy, r * 0.82, fill=1, stroke=0)


def _scatter_stars(c, n=45, seed=0):
    import random
    rng = random.Random(seed)
    # Nebula cloud layers (soft colour volumes for depth)
    nebula = [
        (rng.uniform(W*0.1, W*0.4), rng.uniform(H*0.55, H*0.85),
         rng.uniform(90, 160), HexColor("#1a1060"), rng.uniform(0.10, 0.17)),
        (rng.uniform(W*0.6, W*0.9), rng.uniform(H*0.15, H*0.50),
         rng.uniform(80, 140), HexColor("#081840"), rng.uniform(0.09, 0.15)),
        (rng.uniform(W*0.35, W*0.65), rng.uniform(H*0.3, H*0.7),
         rng.uniform(110, 190), HexColor("#0f0830"), rng.uniform(0.07, 0.13)),
    ]
    for nx, ny, nr, ncol, nalpha in nebula:
        c.setFillColor(ncol)
        c.setFillAlpha(nalpha)
        c.circle(nx, ny, nr, fill=1, stroke=0)
    c.setFillAlpha(1.0)
    # Point stars
    for _ in range(n):
        x = rng.uniform(MG + 15, W - MG - 15)
        y = rng.uniform(MG + 15, H - MG - 15)
        r = rng.uniform(0.6, 2.8)
        alpha = rng.uniform(0.14, 0.75)
        col = GLD if rng.random() > 0.45 else SLV
        c.setFillColor(col)
        c.setFillAlpha(alpha)
        c.circle(x, y, r, fill=1, stroke=0)
    # Bright sparkle stars (4-pointed)
    for _ in range(5):
        sx = rng.uniform(MG + 25, W - MG - 25)
        sy = rng.uniform(MG + 25, H - MG - 25)
        _star(c, sx, sy, rng.uniform(2.5, 4.5), 4, GLD2)
    c.setFillAlpha(1.0)


def _double_border(c, x, y, w, h, col=None, bg=None, gap=5, radius=6):
    """Layered gold border with bevel + gloss effect."""
    col = col or GLD
    if bg is not None:
        c.setFillColor(bg)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=0)
    # Shadow/depth layer (dark gold, slightly larger)
    c.setStrokeColor(GLD_DARK)
    c.setLineWidth(3.5)
    c.setStrokeAlpha(0.40)
    c.roundRect(x, y, w, h, radius, fill=0, stroke=1)
    c.setStrokeAlpha(1.0)
    # Main border
    c.setStrokeColor(col)
    c.setLineWidth(1.6)
    c.roundRect(x, y, w, h, radius, fill=0, stroke=1)
    # Bright highlight stroke
    c.setStrokeColor(GLD_LITE)
    c.setLineWidth(0.55)
    c.setStrokeAlpha(0.55)
    c.roundRect(x, y, w, h, radius, fill=0, stroke=1)
    c.setStrokeAlpha(1.0)
    # Inner border
    c.setStrokeColor(col)
    c.setLineWidth(0.65)
    c.roundRect(x + gap, y + gap, w - 2*gap, h - 2*gap,
                max(radius - 2, 2), fill=0, stroke=1)
    # Top-edge gloss strip (simulates curved light catch)
    c.setFillColor(GLD_LITE)
    c.setFillAlpha(0.07)
    c.roundRect(x + gap + 2, y + h - gap - 3, w - 2*gap - 4, 3, 2, fill=1, stroke=0)
    c.setFillAlpha(1.0)


def _corner_stars(c, x, y, w, h, r=7):
    for px, py in [(x+14, y+14), (x+w-14, y+14), (x+14, y+h-14), (x+w-14, y+h-14)]:
        # Glow behind corner ornament
        c.setFillColor(GLD2)
        c.setFillAlpha(0.18)
        c.circle(px, py, r + 4, fill=1, stroke=0)
        c.setFillAlpha(1.0)
        _star(c, px, py, r, 4, GLD2)
        _star(c, px, py, r * 0.55, 4, GLD_LITE)
    # Mid-side small ornaments
    for px, py in [(x + w/2, y + 10), (x + w/2, y + h - 10),
                   (x + 10, y + h/2), (x + w - 10, y + h/2)]:
        _star(c, px, py, r * 0.5, 4, GLD)


def _hline(c, y, x1=None, x2=None, col=None, lw=0.7):
    x1 = x1 if x1 is not None else MG + BDG + 5
    x2 = x2 if x2 is not None else W - MG - BDG - 5
    col = col or GLD
    # Shadow below (depth/bevel)
    c.setStrokeColor(GLD_DARK)
    c.setLineWidth(lw + 1.1)
    c.setStrokeAlpha(0.28)
    c.line(x1, y - 0.5, x2, y - 0.5)
    c.setStrokeAlpha(1.0)
    # Main gold line
    c.setStrokeColor(col)
    c.setLineWidth(lw)
    c.line(x1, y, x2, y)
    # Bright centre highlight (light from above)
    c.setStrokeColor(GLD_LITE)
    c.setLineWidth(max(lw * 0.28, 0.22))
    c.setStrokeAlpha(0.58)
    c.line(x1, y + max(lw * 0.28, 0.28), x2, y + max(lw * 0.28, 0.28))
    c.setStrokeAlpha(1.0)


def _diamond_divider(c, y, x1=None, x2=None):
    xl = (x1 if x1 is not None else MG + BDG + 5)
    xr = (x2 if x2 is not None else W - MG - BDG - 5)
    # Triple-line style (thin dark + bright main + thin dark, like the reference)
    c.setStrokeColor(GLD_DARK)
    c.setLineWidth(0.35)
    c.setStrokeAlpha(0.45)
    c.line(xl, y + 3.0, xr, y + 3.0)
    c.line(xl, y - 3.0, xr, y - 3.0)
    c.setStrokeAlpha(1.0)
    # Main metallic centre line
    _hline(c, y, xl, xr, col=GLD, lw=1.0)
    # End ornaments
    _star(c, xl - 6, y, 5, 4, GLD2)
    _star(c, xr + 6, y, 5, 4, GLD2)


def _gold_gradient_fill(c, x, y, w, h, radius=0, steps=10):
    """Simulate metallic vertical gradient: dark edges → bright centre → dark edges."""
    for i in range(steps):
        t = (i + 0.5) / steps          # 0 = bottom, 1 = top
        brightness = 1.0 - (2*t - 1)**2  # 0→0, 0.5→1.0, 1→0 (quadratic peak at centre)
        sy = y + i * h / steps
        sh = h / steps + 0.6
        if brightness > 0.55:
            c.setFillColor(GLD_LITE)
            c.setFillAlpha(brightness * 0.38)
        else:
            c.setFillColor(GLD_DARK)
            c.setFillAlpha((1.0 - brightness) * 0.22)
        if radius > 0:
            c.roundRect(x, sy, w, sh, radius, fill=1, stroke=0)
        else:
            c.rect(x, sy, w, sh, fill=1, stroke=0)
    c.setFillAlpha(1.0)


# ─── Text helpers ──────────────────────────────────────────────────────────

def _t(c, x, y, text, font=None, size=12, col=None, align="left"):
    c.setFont(font or FN, size)
    c.setFillColor(col or WHT)
    if align == "center":
        c.drawCentredString(x, y, text)
    elif align == "right":
        c.drawRightString(x, y, text)
    else:
        c.drawString(x, y, text)


def _afs(text, font, max_s, min_s, max_w):
    """Largest font size where text fits within max_w."""
    s = max_s
    while s >= min_s:
        if SW(text, font, s) <= max_w:
            return s
        s -= 0.5
    return min_s


def _wrap(text, font, size, max_w):
    """Character-accurate text wrapping for Japanese."""
    lines = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        cur = ""
        for ch in para:
            if SW(cur + ch, font, size) <= max_w:
                cur += ch
            else:
                if cur:
                    lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
    return lines


def _draw_wrapped(c, text, x, y, font, size, col, max_w, lh, bottom=None):
    """Draw wrapped text block; returns final y position."""
    c.setFont(font, size)
    c.setFillColor(col)
    for line in _wrap(text, font, size, max_w):
        if bottom is not None and y - lh < bottom:
            break
        c.drawString(x, y, line)
        y -= lh
    return y


# ─── Page base (background + full-page double border) ─────────────────────

def _page_base(c, seed=0):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    _scatter_stars(c, n=50, seed=seed)
    # Outer border — shadow layer
    c.setStrokeColor(GLD_DARK)
    c.setLineWidth(4.2)
    c.setStrokeAlpha(0.35)
    c.rect(MG - 1, MG - 1, W - 2*MG + 2, H - 2*MG + 2, fill=0, stroke=1)
    c.setStrokeAlpha(1.0)
    # Outer border — main gold
    c.setStrokeColor(GLD)
    c.setLineWidth(1.8)
    c.rect(MG, MG, W - 2*MG, H - 2*MG, fill=0, stroke=1)
    # Outer border — bright highlight
    c.setStrokeColor(GLD_LITE)
    c.setLineWidth(0.5)
    c.setStrokeAlpha(0.45)
    c.rect(MG, MG, W - 2*MG, H - 2*MG, fill=0, stroke=1)
    c.setStrokeAlpha(1.0)
    # Inner border
    c.setStrokeColor(GLD)
    c.setLineWidth(0.65)
    c.rect(MG + BDG, MG + BDG, W - 2*(MG + BDG), H - 2*(MG + BDG), fill=0, stroke=1)
    # Metallic gradient fill on top and bottom border bands
    band = BDG + 4
    _gold_gradient_fill(c, MG, H - MG - band, W - 2*MG, band)   # top band
    _gold_gradient_fill(c, MG, MG, W - 2*MG, band)               # bottom band
    _corner_stars(c, MG, MG, W - 2*MG, H - 2*MG, r=9)


def _page_header(c, left="", center="", right=""):
    """Standard header band (used on content pages 2–5)."""
    _hline(c, HDR_LINE, lw=0.9)
    if left:
        _t(c, MG + BDG + 12, HDR_LINE + 10, left, FN, 8, GLD)
    if center:
        _t(c, W/2, HDR_LINE + 12, center, FNB, 11, GLD2, "center")
    if right:
        _t(c, W - MG - BDG - 12, HDR_LINE + 10, right, FN, 8, SLV, "right")
    # Small stars flanking center
    _star(c, W/2 - SW(center, FNB, 11)/2 - 14, HDR_LINE + 16, 5, 5, GLD)
    _star(c, W/2 + SW(center, FNB, 11)/2 + 14, HDR_LINE + 16, 5, 5, GLD)


def _page_footer(c, page_num=1, total=6):
    """Standard footer band."""
    _hline(c, FTR_LINE, lw=0.8)
    # Text at FTR_LINE-14 keeps descenders (3pt) above inner border bottom (y=29)
    _t(c, W/2, FTR_LINE - 14, f"― {page_num} / {total} ―", FN, 9, DIM, "center")
    _t(c, MG + BDG + 12, FTR_LINE - 14, "星詠みChronicle", FN, 8, DIM)
    _star(c, MG + BDG + 6, FTR_LINE - 8, 4, 5, GLD)
    _star(c, W - MG - BDG - 6, FTR_LINE - 8, 4, 5, GLD)


# ─── Image drawing with fallback frame ────────────────────────────────────

def _draw_img_raw(c, path, x, y, w, h):
    """Draw image; returns True on success."""
    if path and os.path.exists(path):
        try:
            c.drawImage(path, x, y, w, h,
                        preserveAspectRatio=True, anchor='c', mask='auto')
            return True
        except Exception:
            pass
    return False


def _img_or_frame(c, path, x, y, w, h, label="", type_id=None, nav=None, frame_col=None):
    """Draw image or golden decorative fallback frame."""
    if _draw_img_raw(c, path, x, y, w, h):
        return

    fc = frame_col or (TC(type_id) if type_id else GLD)
    # Background
    c.setFillColor(PRP3)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=0)
    # Double border
    _double_border(c, x, y, w, h, col=fc, gap=6, radius=8)
    # Corner ornaments
    _corner_stars(c, x, y, w, h, r=6)

    cx, cy = x + w/2, y + h/2
    r = min(w, h) * 0.28
    c.setFillColor(PRP2)
    c.circle(cx, cy, r + 3, fill=1, stroke=0)
    c.setStrokeColor(fc)
    c.setLineWidth(1.2)
    c.circle(cx, cy, r + 3, fill=0, stroke=1)

    # Center symbol
    if type_id:
        syms = {1:"炎",2:"海",3:"雷",4:"森",5:"月",6:"陽",
                7:"岳",8:"嵐",9:"花",10:"氷",11:"地",12:"星"}
        sym = syms.get(type_id, "◆")
        fs = min(w, h) * 0.22
        _t(c, cx, cy - fs*0.35, sym, FNB, fs, TC(type_id), "center")
    elif nav:
        nav_sym = {"叢雲":"雲", "ノヴァ":"星", "フレイヤ":"猫", "グレイス":"氷"}
        sym = nav_sym.get(nav, "◆")
        fs = min(w, h) * 0.22
        _t(c, cx, cy - fs*0.35, sym, FNB, fs, GLD2, "center")

    # Label at bottom of frame
    if label:
        fs2 = _afs(label, FN, 10, 7, w - 16)
        _t(c, cx, y + 10, label, FN, fs2, SLV, "center")


# ─── Score bar component ───────────────────────────────────────────────────

def _score_bar(c, x, y, score, bar_w=240, bar_h=13):
    """Draw a glossy score progress bar."""
    # Track — dark inset shadow
    c.setFillColor(BG)
    c.setFillAlpha(0.55)
    c.roundRect(x + 1, y - 1, bar_w, bar_h, bar_h / 2, fill=1, stroke=0)
    c.setFillAlpha(1.0)
    # Track body
    c.setFillColor(PRP3)
    c.setStrokeColor(GLD_DARK)
    c.setLineWidth(0.7)
    c.roundRect(x, y, bar_w, bar_h, bar_h / 2, fill=1, stroke=1)
    # Fill
    fw = bar_w * score / 100
    if fw > 2:
        fc = GLD  if score >= 85 else \
             HexColor("#9b7914") if score >= 70 else PRP
        c.setFillColor(fc)
        c.roundRect(x, y, fw, bar_h, bar_h / 2, fill=1, stroke=0)
        # Bottom shadow band (gives cylindrical depth)
        c.setFillColor(GLD_DARK)
        c.setFillAlpha(0.28)
        c.roundRect(x, y, fw, bar_h * 0.38, bar_h / 2, fill=1, stroke=0)
        c.setFillAlpha(1.0)
        # Main gloss shine strip
        c.setFillColor(GLD_LITE)
        c.setFillAlpha(0.38)
        shine_h = bar_h * 0.38
        c.roundRect(x + 2, y + bar_h * 0.54, max(fw - 4, 0), shine_h, 2,
                    fill=1, stroke=0)
        c.setFillAlpha(1.0)
        # Bright tip glow
        tip_w = min(24, fw)
        c.setFillColor(GLD_LITE)
        c.setFillAlpha(0.50)
        c.roundRect(x + fw - tip_w, y, tip_w, bar_h, bar_h / 2, fill=1, stroke=0)
        c.setFillAlpha(1.0)
        # Border on fill
        c.setStrokeColor(GLD2)
        c.setLineWidth(0.5)
        c.roundRect(x, y, fw, bar_h, bar_h / 2, fill=0, stroke=1)
    # Score label
    _t(c, x + bar_w + 9, y + 2, f"{score}点", FNB, 12, GLD3)
    # Star rating
    stars = min(5, max(1, round(score / 20)))
    for i in range(5):
        _star(c, x + bar_w + 55 + i * 15, y + bar_h/2, 6, 5,
              GLD3 if i < stars else DIM)


# ─── Section box component ─────────────────────────────────────────────────

def _section_box(c, x, y, w, h, title="", accent=None):
    """Section box with jewel-like gloss and layered borders."""
    accent = accent or GLD
    # Base fill
    c.setFillColor(BG3)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=0)
    # Upper-half inner glow (jewel glass effect)
    c.setFillColor(accent)
    c.setFillAlpha(0.055)
    c.roundRect(x + 3, y + h // 2, w - 6, h // 2 - 3, 4, fill=1, stroke=0)
    c.setFillAlpha(1.0)
    # Bottom shadow darkening
    c.setFillColor(BG)
    c.setFillAlpha(0.22)
    c.roundRect(x + 3, y + 3, w - 6, h // 4, 3, fill=1, stroke=0)
    c.setFillAlpha(1.0)
    # Double border (now includes shadow + highlight layers)
    _double_border(c, x, y, w, h, col=accent, gap=4, radius=6)
    # Left accent stripe — base + metallic gradient
    c.setFillColor(accent)
    c.roundRect(x, y, 5, h, 3, fill=1, stroke=0)
    _gold_gradient_fill(c, x, y, 5, h, radius=3)
    # Title badge
    if title:
        tw = SW(title, FNB, 10) + 16
        # Badge shadow
        c.setFillColor(GLD_DARK)
        c.setFillAlpha(0.50)
        c.roundRect(x + 13, y + h - 20, tw, 20, 5, fill=1, stroke=0)
        c.setFillAlpha(1.0)
        # Badge base
        c.setFillColor(accent)
        c.roundRect(x + 12, y + h - 19, tw, 20, 5, fill=1, stroke=0)
        # Metallic gradient on badge
        _gold_gradient_fill(c, x + 12, y + h - 19, tw, 20, radius=5)
        _t(c, x + 12 + tw/2, y + h - 14, title, FNB, 10, BG, "center")


# ─── Circular clip + cover-fit image drawing ──────────────────────────────

def _circle_clip_path(c, cx, cy, r):
    """Return a bezier-approximated circle path for use with clipPath."""
    k = 0.5522847498   # cubic bezier kappa
    p = c.beginPath()
    p.moveTo(cx + r, cy)
    p.curveTo(cx + r,   cy + r*k, cx + r*k, cy + r,   cx,     cy + r)
    p.curveTo(cx - r*k, cy + r,   cx - r,   cy + r*k, cx - r, cy)
    p.curveTo(cx - r,   cy - r*k, cx - r*k, cy - r,   cx,     cy - r)
    p.curveTo(cx + r*k, cy - r,   cx + r,   cy - r*k, cx + r, cy)
    p.close()
    return p


def _draw_circle_cover(c, img_path, cx, cy, r):
    """Draw image cover-fit inside a circular clip. Returns True on success."""
    if not img_path or not os.path.exists(img_path):
        return False
    try:
        from PIL import Image as PILImage
        with PILImage.open(img_path) as pil:
            iw, ih = pil.size
        diam  = r * 2
        scale = max(diam / iw, diam / ih)   # cover: larger side fills circle
        dw, dh = iw * scale, ih * scale
        c.saveState()
        c.clipPath(_circle_clip_path(c, cx, cy, r), stroke=0, fill=0)
        c.drawImage(img_path, cx - dw/2, cy - dh/2, dw, dh, mask='auto')
        c.restoreState()
        return True
    except Exception:
        return False


def _ornate_ring(c, cx, cy, r, col):
    """Multi-layer baroque-style ring: shadow → main gold → highlight → outer ring with dots."""
    # Deep shadow ring (bevel depth)
    c.setStrokeColor(GLD_DARK)
    c.setLineWidth(5.0)
    c.setStrokeAlpha(0.42)
    c.circle(cx, cy, r + 5, fill=0, stroke=1)
    c.setStrokeAlpha(1.0)
    # Main gold ring
    c.setStrokeColor(col)
    c.setLineWidth(2.8)
    c.circle(cx, cy, r + 4, fill=0, stroke=1)
    # Bright highlight ring
    c.setStrokeColor(GLD_LITE)
    c.setLineWidth(0.75)
    c.setStrokeAlpha(0.60)
    c.circle(cx, cy, r + 4, fill=0, stroke=1)
    c.setStrokeAlpha(1.0)
    # Inner accent ring
    c.setStrokeColor(col)
    c.setLineWidth(1.0)
    c.setStrokeAlpha(0.55)
    c.circle(cx, cy, r + 1, fill=0, stroke=1)
    c.setStrokeAlpha(1.0)
    # Outer decorative ring
    c.setStrokeColor(GLD2)
    c.setLineWidth(0.55)
    c.circle(cx, cy, r + 14, fill=0, stroke=1)
    # Decorative dots at 8 cardinal/intercardinal positions
    for i in range(8):
        angle = math.pi / 8 + i * math.pi / 4
        dx = cx + (r + 14) * math.cos(angle)
        dy = cy + (r + 14) * math.sin(angle)
        c.setFillColor(GLD2)
        c.circle(dx, dy, 2.2, fill=1, stroke=0)
    # Metallic torus highlight: bright arc at top of ring (simulates light from above)
    rr = r + 4
    c.setStrokeColor(GLD_LITE)
    c.setLineWidth(2.0)
    c.setStrokeAlpha(0.50)
    c.arc(cx - rr, cy - rr, cx + rr, cy + rr, startAng=35, extent=110)
    c.setStrokeAlpha(1.0)
    # Dark shadow arc at bottom
    c.setStrokeColor(GLD_DARK)
    c.setLineWidth(1.5)
    c.setStrokeAlpha(0.35)
    c.arc(cx - rr, cy - rr, cx + rr, cy + rr, startAng=215, extent=110)
    c.setStrokeAlpha(1.0)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 0 ── COVER
# ════════════════════════════════════════════════════════════════════════════

def _page_cover(c, data):
    tid = data["type_id"]
    _page_base(c, seed=tid * 17)

    acc = TC(tid)
    name = data["name"]

    # ── Decorative moon (top-right) ──
    _moon(c, W - 68, H - 68, 44, GLD)
    _star(c, 68, H - 68, 22, 5, GLD)
    _star(c, 52, H - 118, 12, 5, SLV)
    _star(c, 105, H - 48, 7, 5, GLD2)

    # ── Site title (serif fonts for elegant fortune-telling look) ──
    title_text = "星 詠 み  Chronicle"
    title_fs = _afs(title_text, FNS, 26, 14, CW - 60)
    # Title backing — gradient gold band
    tw_px = SW(title_text, FNS, title_fs)
    bx = W/2 - tw_px/2 - 18
    bw = tw_px + 36
    c.setFillColor(GLD_DARK)
    c.setFillAlpha(0.18)
    c.roundRect(bx, H - 82, bw, 28, 6, fill=1, stroke=0)
    c.setFillAlpha(1.0)
    _gold_gradient_fill(c, bx, H - 82, bw, 28, radius=6)
    c.setStrokeColor(GLD2)
    c.setLineWidth(0.6)
    c.setStrokeAlpha(0.55)
    c.roundRect(bx, H - 82, bw, 28, 6, fill=0, stroke=1)
    c.setStrokeAlpha(1.0)
    _t(c, W/2, H - 72, title_text, FNS, title_fs, GLD2, "center")
    _t(c, W/2, H - 92, "〜  Personal Fortune Reading  〜", FN, 9, SLV, "center")
    _diamond_divider(c, H - 105)

    # ── Person name ──
    name_text = f"◆  {name}  様"
    name_fs = _afs(name_text, FNB, 22, 12, CW - 80)
    _t(c, W/2, H - 138, name_text, FNB, name_fs, GLD3, "center")
    _t(c, W/2, H - 160, "個  人  鑑  定  書", FNB, 13, SLV, "center")

    # ── Character image (large, centered) ──
    img_cx = W / 2
    img_cy = H - 345      # center of image circle
    img_r  = 128          # radius of circular image area
    img_path = _type_img_path(tid)

    # Nebula glow behind character (blue layer + accent layer)
    for i in range(7, 0, -1):
        c.setFillColor(HexColor("#1a1060"))
        c.setFillAlpha(0.05 * i)
        c.circle(img_cx, img_cy, img_r + i * 18, fill=1, stroke=0)
    for i in range(5, 0, -1):
        c.setFillColor(acc)
        c.setFillAlpha(0.035 * i)
        c.circle(img_cx, img_cy, img_r + i * 14, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    # Dark circle backing
    c.setFillColor(PRP3)
    c.circle(img_cx, img_cy, img_r + 6, fill=1, stroke=0)

    # Image or fallback symbol
    if not _draw_circle_cover(c, img_path, img_cx, img_cy, img_r):
        syms = {1:"炎",2:"海",3:"雷",4:"森",5:"月",6:"陽",
                7:"岳",8:"嵐",9:"花",10:"氷",11:"地",12:"星"}
        c.setFillColor(PRP2)
        c.circle(img_cx, img_cy, img_r - 8, fill=1, stroke=0)
        _t(c, img_cx, img_cy - 24, syms.get(tid, "◆"), FNB, 64, acc, "center")

    # Ornate multi-layer ring
    _ornate_ring(c, img_cx, img_cy, img_r, GLD)
    # Ring stars at outer radius
    for i in range(8):
        angle = math.pi/8 + i * math.pi/4
        sx = img_cx + (img_r + 28) * math.cos(angle)
        sy = img_cy + (img_r + 28) * math.sin(angle)
        _star(c, sx, sy, 5, 5, GLD if i % 2 == 0 else SLV)

    # ── Type name ──
    # Ring stars sit at radius img_r+24; bottom-most is at angle ~270°-ish.
    # Lowest star y = img_cy - (img_r+24)*sin(3π/8).  Add 5pt for star radius.
    ring_bottom_y = img_cy - (img_r + 28) * math.sin(3 * math.pi / 8) - 10
    text_y = ring_bottom_y - 16
    type_text = f"◆  {data['type']['name']}  ◆"
    type_fs = _afs(type_text, FNB, 28, 15, CW - 80)
    _t(c, W/2, text_y, type_text, FNB, type_fs, GLD3, "center")
    kw_text = data["type"]["keyword"]
    _t(c, W/2, text_y - 22, kw_text, FN, 11, SLV, "center")
    _diamond_divider(c, text_y - 36)

    # ── Main info box ──
    box_top = text_y - 46
    box_h = 68
    box_y = box_top - box_h
    _double_border(c, CX1 + 18, box_y, CW - 36, box_h, bg=PRP2, gap=5)
    _gold_gradient_fill(c, CX1 + 18, box_y, CW - 36, box_h, radius=6)
    _t(c, W/2, box_y + box_h - 22,
       f"生年月日：{data['birth']}　血液型：{data['blood']['type']}型",
       FN, 11, WHT, "center")
    _t(c, W/2, box_y + box_h - 42,
       f"星座：{data['zodiac']['name']}　干支：{data['chinese']['name']}　数秘：{data['life_path']['number']}",
       FN, 11, WHT, "center")
    _t(c, W/2, box_y + 10,
       f"鑑定月：{data['month_str']}",
       FN, 10, GLD, "center")

    # ── Navigator image section ──
    nav_colors = {"叢雲": HexColor("#8888ff"), "ノヴァ": HexColor("#ff8844"),
                  "フレイヤ": HexColor("#66cc66"), "グレイス": HexColor("#88aacc")}
    nc = nav_colors.get(data["navigator"], GLD)

    nav_strip_top = box_y - 8
    nav_strip_bot = FTR_LINE + 14
    nav_strip_h   = nav_strip_top - nav_strip_bot
    nav_r  = min(56, max(22, nav_strip_h // 2 - 16))
    nav_cx = W / 2
    nav_cy = nav_strip_bot + nav_r + 22   # anchor from bottom for lower placement

    # Thin separator above navigator area
    _hline(c, nav_strip_top, lw=0.5)

    # Subtle glow
    c.setFillColor(nc)
    c.setFillAlpha(0.07)
    c.circle(nav_cx, nav_cy, nav_r + 22, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    # Dark backing circle
    c.setFillColor(PRP3)
    c.circle(nav_cx, nav_cy, nav_r + 4, fill=1, stroke=0)

    # Navigator image (circular clip)
    nav_path = _nav_img_path(data["navigator"])
    if not _draw_circle_cover(c, nav_path, nav_cx, nav_cy, nav_r):
        nav_syms = {"叢雲": "雲", "ノヴァ": "星", "フレイヤ": "猫", "グレイス": "氷"}
        c.setFillColor(PRP2)
        c.circle(nav_cx, nav_cy, nav_r - 6, fill=1, stroke=0)
        _t(c, nav_cx, nav_cy - 16, nav_syms.get(data["navigator"], "◆"), FNB, 36, nc, "center")

    # Gold ring
    c.setStrokeColor(nc)
    c.setLineWidth(2.0)
    c.circle(nav_cx, nav_cy, nav_r + 3, fill=0, stroke=1)

    # Name label below circle (clear of ring bottom)
    _t(c, W/2, nav_cy - nav_r - 20,
       f"◆  ニャビゲーター：{data['navigator']}  ◆", FN, 11, nc, "center")

    # Bottom corner stars
    _star(c, MG + 18, MG + 18, 10, 5, GLD)
    _star(c, W - MG - 18, MG + 18, 10, 5, GLD)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 ── 四軸分析
# ════════════════════════════════════════════════════════════════════════════

def _page_four_axis(c, data):
    _page_base(c, seed=7)
    _page_header(c, "星詠みChronicle", "◆  四 軸 分 析  ◆", data["name"] + " 様")
    _page_footer(c, 2, 5)

    # Sub-title
    _t(c, W/2, CY2 - 14, "あなたを形作る 4 つの力の流れ", FNS, 10, SLV, "center")
    _diamond_divider(c, CY2 - 28)

    sections = [
        ("星　座",
         data["zodiac"]["symbol"] + "  " + data["zodiac"]["name"],
         f"元素：{data['zodiac']['element']}　キーワード：{data['zodiac']['keyword']}",
         data["zodiac"]["desc"],
         HexColor("#ffe060")),
        ("干　支",
         data["chinese"]["name"],
         f"元素：{data['chinese']['element']}　キーワード：{data['chinese']['keyword']}",
         data["chinese"]["desc"],
         HexColor("#e8b040")),
        ("数 秘 術",
         f"ライフパスナンバー  {data['life_path']['number']}",
         f"キーワード：{data['life_path']['keyword']}",
         data["life_path"]["desc"],
         HexColor("#c088ff")),
        ("血 液 型",
         f"{data['blood']['type']} 型",
         f"キーワード：{data['blood']['keyword']}",
         data["blood"]["desc"],
         HexColor("#ff8888")),
    ]

    n   = len(sections)
    gap = 12
    top_y  = CY2 - 36
    avail  = top_y - CY1
    sh     = (avail - gap * (n - 1)) / n   # section height ≈ 162 pt

    for i, (title, main, sub, desc, accent) in enumerate(sections):
        sy = top_y - i * (sh + gap) - sh

        _section_box(c, CX1, sy, CW, sh, title, accent)

        # Main label (auto-sized)
        main_fs = _afs(main, FNB, 19, 10, CW - 30)
        _t(c, CX1 + 18, sy + sh - 58, main, FNB, main_fs, WHT)

        # Sub label
        sub_fs = _afs(sub, FN, 10, 8, CW - 30)
        _t(c, CX1 + 18, sy + sh - 77, sub, FN, sub_fs, GLD)

        # Thin accent line
        c.setStrokeColor(accent)
        c.setLineWidth(0.35)
        c.line(CX1 + 14, sy + sh - 89, CX1 + CW - 14, sy + sh - 89)

        # Description (wrapped, truncated to box)
        _draw_wrapped(c, desc, CX1 + 18, sy + sh - 106,
                      FNS, 10.5, SLV, CW - 32, 16, sy + 8)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 ── 今月の運勢
# ════════════════════════════════════════════════════════════════════════════

def _page_fortune(c, data):
    _page_base(c, seed=99)
    tid = data["type_id"]
    _page_header(c, "星詠みChronicle", "◆  今 月 の 運 勢  ◆", data["month_str"])
    _page_footer(c, 3, 5)

    # Sub-title
    sub_text = f"◆  {data['name']}様の今月の星の流れ"
    sub_fs = _afs(sub_text, FN, 11, 8, CW)
    _t(c, CX1, CY2 - 14, sub_text, FN, sub_fs, GLD)
    _diamond_divider(c, CY2 - 28)

    cats   = ["総合", "恋愛", "金運", "仕事"]
    labels = {"総合": "総合運", "恋愛": "恋愛運", "金運": "金　運", "仕事": "仕事運"}
    icons  = {"総合": "◆", "恋愛": "●", "金運": "◆", "仕事": "★"}

    n    = len(cats)
    gap  = 10
    top_y = CY2 - 36
    avail = top_y - CY1
    bh    = (avail - gap * (n - 1)) / n   # block height ≈ 163 pt

    for i, cat in enumerate(cats):
        score = data["scores"][cat]
        msg   = data["type"]["fortune_messages"][cat]
        by    = top_y - i * (bh + gap) - bh

        # Block background
        c.setFillColor(BG2)
        c.roundRect(CX1, by, CW, bh, 7, fill=1, stroke=0)
        # Upper-half jewel glow
        c.setFillColor(TC(tid))
        c.setFillAlpha(0.04)
        c.roundRect(CX1 + 3, by + bh // 2, CW - 6, bh // 2 - 3, 5, fill=1, stroke=0)
        c.setFillAlpha(1.0)
        # Shadow layer
        c.setStrokeColor(GLD_DARK)
        c.setLineWidth(3.2)
        c.setStrokeAlpha(0.35)
        c.roundRect(CX1, by, CW, bh, 7, fill=0, stroke=1)
        c.setStrokeAlpha(1.0)
        # Main border
        c.setStrokeColor(GLD)
        c.setLineWidth(0.9)
        c.roundRect(CX1, by, CW, bh, 7, fill=0, stroke=1)
        # Highlight border
        c.setStrokeColor(GLD_LITE)
        c.setLineWidth(0.4)
        c.setStrokeAlpha(0.45)
        c.roundRect(CX1, by, CW, bh, 7, fill=0, stroke=1)
        c.setStrokeAlpha(1.0)
        # Inner thin border
        c.setStrokeColor(GLD)
        c.setLineWidth(0.35)
        c.roundRect(CX1 + 4, by + 4, CW - 8, bh - 8, 4, fill=0, stroke=1)
        # Left accent stripe
        c.setFillColor(TC(tid))
        c.roundRect(CX1, by, 5, bh, 3, fill=1, stroke=0)

        # Category header
        cat_text = f"{icons[cat]}  {labels[cat]}"
        _t(c, CX1 + 16, by + bh - 22, cat_text, FNB, 14, GLD2)

        # Score bar  (label + bar)
        bar_y  = by + bh - 44   # bar bottom y
        _t(c, CX1 + 16, bar_y + 3, "スコア", FN, 9, GLD)
        _score_bar(c, CX1 + 62, bar_y, score, bar_w=215, bar_h=13)

        # Thin separator
        c.setStrokeColor(PRP2)
        c.setLineWidth(0.35)
        c.line(CX1 + 12, by + bh - 55, CX1 + CW - 12, by + bh - 55)

        # Message text (wrapped, constrained to box)
        _draw_wrapped(c, msg, CX1 + 16, by + bh - 70,
                      FNS, 10, WHT, CW - 28, 15, by + 7)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 ── ニャビゲーター & 開運情報（合体ページ）
# ════════════════════════════════════════════════════════════════════════════

def _page_nav_lucky(c, data):
    _page_base(c, seed=55)
    nav     = data["navigator"]
    nav_msg = get_navigator_message(nav, data["type_id"], data["name"])
    td      = data["type"]
    tid     = data["type_id"]

    nav_accent = {
        "叢雲":   HexColor("#9999ff"),
        "ノヴァ":  HexColor("#ff8844"),
        "フレイヤ": HexColor("#66cc66"),
        "グレイス": HexColor("#88bbcc"),
    }.get(nav, GLD)

    _page_header(c, "星詠みChronicle",
                 f"◆  ニャビゲーター  &  開 運 情 報  ◆", data["name"] + " 様")
    _page_footer(c, 4, 5)

    _t(c, W/2, CY2 - 15, nav_msg["header"], FNS, 12, GLD2, "center")
    _diamond_divider(c, CY2 - 30)

    content_top = CY2 - 38
    content_h   = content_top - CY1   # ≈ 677 pt
    gap = 10

    # ── UPPER 47%: Navigator image (left) + message (right) ──
    upper_h  = int(content_h * 0.47)
    upper_y1 = content_top - upper_h

    lw       = 180
    nav_path = _nav_img_path(nav)
    c.setFillColor(PRP3)
    c.roundRect(CX1, upper_y1, lw, upper_h, 10, fill=1, stroke=0)
    _double_border(c, CX1, upper_y1, lw, upper_h, col=nav_accent, gap=6, radius=10)
    pad = 10
    _img_or_frame(c, nav_path,
                  CX1 + pad, upper_y1 + pad + 28,
                  lw - pad*2, upper_h - pad*2 - 38,
                  nav, nav=nav, frame_col=nav_accent)
    _t(c, CX1 + lw/2, upper_y1 + 20, nav, FNS, 14, nav_accent, "center")

    rx = CX1 + lw + 14
    rw = CX2 - rx

    intro_fs = _afs(nav_msg["intro"], FNS, 11, 8, rw)
    _t(c, rx, content_top - 18, nav_msg["intro"], FNS, intro_fs, GLD)

    msg_box_h = (content_top - 38) - upper_y1
    _double_border(c, rx, upper_y1, rw, msg_box_h, col=nav_accent, bg=PRP3, gap=6)

    c.setFont(FNS, 42)
    c.setFillColor(nav_accent)
    c.setFillAlpha(0.22)
    c.drawString(rx + 8, upper_y1 + msg_box_h - 32, "「")
    c.setFillAlpha(1.0)

    _draw_wrapped(
        c, nav_msg["message"],
        rx + 18, upper_y1 + msg_box_h - 50,
        FNS, 11, WHT, rw - 30, 21,
        bottom=upper_y1 + 14,
    )

    # ── Divider ──
    _diamond_divider(c, upper_y1 - gap // 2)

    # ── LOWER 53%: Lucky items + colors (top row) + advice (bottom) ──
    lower_top = upper_y1 - gap
    lower_h   = lower_top - CY1

    items  = td["lucky_items"]
    colors = td["lucky_colors"]

    row_h = 100   # items box and colors box side by side
    adv_h = lower_h - row_h - gap

    # Items (left half) and Colors (right half) in one row
    row_y  = lower_top - row_h
    half_w = (CW - gap) / 2

    _section_box(c, CX1, row_y, half_w, row_h, "◆  ラッキーアイテム")
    for j, item in enumerate(items):
        iy = row_y + row_h - 38 - j * 24
        if iy > row_y + 8:
            _star(c, CX1 + 16, iy + 5, 4, 5, GLD2)
            _t(c, CX1 + 28, iy, item, FN, 10, WHT)

    col_x = CX1 + half_w + gap
    _section_box(c, col_x, row_y, half_w, row_h, "◆  ラッキーカラー")
    n_col      = len(colors)
    sw_spacing = (half_w - 20) / n_col
    sw_w       = sw_spacing - 8
    sw_h       = max(34, row_h - 48)
    sw_y       = row_y + 24
    for j, (cname, chex) in enumerate(colors):
        sx = col_x + 10 + j * sw_spacing
        c.setFillColor(HexColor(chex))
        c.setStrokeColor(GLD)
        c.setLineWidth(0.7)
        c.roundRect(sx, sw_y, sw_w, sw_h, 5, fill=1, stroke=1)
        cname_fs = _afs(cname, FN, 9, 7, sw_w)
        _t(c, sx + sw_w/2, row_y + 8, cname, FN, cname_fs, WHT, "center")

    # Advice box (full width, character image on right)
    ay = CY1
    _section_box(c, CX1, ay, CW, adv_h, "★  今月のアドバイス")

    img_r  = min(60, adv_h // 2 - 18)
    img_cx = CX2 - img_r - 14
    img_cy = ay + adv_h // 2
    drawn  = _draw_circle_cover(c, _type_img_path(tid), img_cx, img_cy, img_r)
    if drawn:
        _ornate_ring(c, img_cx, img_cy, img_r, TC(tid))
    else:
        _img_or_frame(c, _type_img_path(tid), img_cx - img_r, ay + 20,
                      img_r * 2, adv_h - 40, td["name"], type_id=tid)

    text_max_w = img_cx - img_r - CX1 - 32

    advice = [f"●  {data['month_str']}、{td['name']}のあなたへ", "", td["desc"], ""]
    advice += [f"◆  {t}" for t in td["traits"]]
    advice += [
        "",
        f"★  星座：{data['zodiac']['name']}　干支：{data['chinese']['name']}　数秘：{data['life_path']['number']}",
        "★  今月の星の流れを活かして、あなたらしい一歩を踏み出しましょう。",
    ]

    ay_cursor = ay + adv_h - 35
    for line in advice:
        if not line:
            ay_cursor -= 5
            continue
        if ay_cursor < ay + 8:
            break
        col_ = GLD if line.startswith("●") else GLD2 if line.startswith("◆") else SLV
        fs_  = 11 if line.startswith("●") else 10
        for wline in _wrap(line, FNS, fs_, text_max_w):
            if ay_cursor < ay + 8:
                break
            _t(c, CX1 + 18, ay_cursor, wline, FNS, fs_, col_)
            ay_cursor -= 17


# ════════════════════════════════════════════════════════════════════════════
# PAGE 5 ── BACK COVER
# ════════════════════════════════════════════════════════════════════════════

def _page_back(c, data):
    _page_base(c, seed=9999)

    # Large moon (center-top area)
    _moon(c, W/2 + 50, H - 150, 78, GLD)
    # Decorative stars constellation
    pts = [
        (W/2 - 80, H - 118),
        (W/2 - 50, H - 210),
        (W/2 + 50, H - 150),
        (W/2 + 105, H - 200),
        (W/2 + 20,  H - 240),
    ]
    for px, py in pts:
        _star(c, px, py, 10, 5, GLD)
    # Constellation lines
    c.setStrokeColor(GLD)
    c.setLineWidth(0.4)
    c.setStrokeAlpha(0.3)
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
    c.setStrokeAlpha(1.0)

    # Upper divider
    _diamond_divider(c, H/2 + 58)

    # Logo (serif for elegant look)
    logo_text = "星 詠 み  Chronicle"
    logo_fs = _afs(logo_text, FNS, 36, 20, CW - 60)
    _t(c, W/2, H/2 + 26, logo_text, FNS, logo_fs, GLD2, "center")
    _t(c, W/2, H/2 + 2, "Hoshiyomi Chronicle", FNSL, 14, SLV, "center")

    _diamond_divider(c, H/2 - 16)

    _t(c, W/2, H/2 - 38,
       "〜 星の導きに従い、あなただけの道を歩んでください 〜",
       FNS, 10, SLV, "center")

    # URL box
    url = "https://hoshiyomi-chronicle.booth.pm"
    url_box_w = 340
    url_box_x = W/2 - url_box_w/2
    _double_border(c, url_box_x, H/2 - 100, url_box_w, 38, bg=PRP2, gap=4)
    _t(c, W/2, H/2 - 78, url, FN, 11, GLD3, "center")

    # Copyright
    _t(c, W/2, H/2 - 118,
       "©  星詠みChronicle  All Rights Reserved",
       FN, 9, DIM, "center")

    # Type name reminder
    _t(c, W/2, H/2 - 140,
       f"◆  {data['name']}様  ／  {data['type']['name']}  ◆",
       FN, 11, GLD, "center")

    # Bottom corner stars
    for sx, sy in [(MG + 20, MG + 20), (W - MG - 20, MG + 20),
                   (MG + 20, H - MG - 20), (W - MG - 20, H - MG - 20)]:
        _star(c, sx, sy, 11, 5, GLD)


# ════════════════════════════════════════════════════════════════════════════
# Main entry point
# ════════════════════════════════════════════════════════════════════════════

def generate_pdf(data: dict, output_path: str = None) -> bytes | None:
    _setup_fonts()

    buf = BytesIO()
    target = str(output_path) if output_path else buf

    cv = _Canvas.Canvas(target, pagesize=A4)
    cv.setTitle(f"星詠みChronicle 個人鑑定書 — {data['name']}様")
    cv.setAuthor("星詠みChronicle")
    cv.setSubject(f"{data['type']['name']} 個人鑑定 {data['month_str']}")

    _page_cover(cv, data);       cv.showPage()   # 表紙
    _page_four_axis(cv, data);  cv.showPage()   # p1 四軸分析
    _page_fortune(cv, data);    cv.showPage()   # p2 運勢スコア
    _page_nav_lucky(cv, data);  cv.showPage()   # p3 ニャビゲーター & 開運情報
    _page_back(cv, data);       cv.showPage()   # 裏表紙

    cv.save()
    if output_path:
        return None
    return buf.getvalue()
