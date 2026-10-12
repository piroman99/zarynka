# -*- coding: utf-8 -*-
"""Кабинет Старика (КБ) — мок-локация (ПОПРИЛИЧНЕЕ: высокий начальник).
Дубовая панель, персидский ковёр, тяжёлый стол с зелёным сукном, кожаное кресло,
портьеры, сейф, библиотека. Пасхалок — РОВНО ДВЕ (выбор заказчика 2026-10-12):
  • дозиметр Р/Ч со стикером «норма» (мем «3,6 Р — не так уж и много»);
  • план «БЛОК №4» на чертёжной доске («четвёртый блок» → ЧАЭС/Сталкер).
Выход: assets/mock/cabinet/kab_base.png + kab_egg_gauge.png + kab_egg_block.png
       + лист assets/review/review_79_starik_kabinet.png
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "mock", "cabinet")
REV = os.path.join(HERE, "assets", "review")
GOTHIC = "/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf"
LATO_B = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
FW, FH = 2400, 1350
random.seed(11)


def f(p, s):
    return ImageFont.truetype(p, s)


def layer():
    return Image.new("RGBA", (FW, FH), (0, 0, 0, 0))


def new_base(top, bot):
    im = Image.new("RGB", (1, FH))
    px = im.load()
    for y in range(FH):
        t = y / (FH - 1)
        px[0, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return im.resize((FW, FH))


def add_vignette(im, strength=0.5):
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse([-w * 0.22, -h * 0.30, w * 1.22, h * 1.30], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w // 10))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(im, dark, Image.eval(mask, lambda v: 255 - int((255 - v) * strength)))


# ============================================================ BASE (приличный кабинет)
im = new_base((60, 46, 34), (34, 26, 20))
d = ImageDraw.Draw(im)

# --- дубовая панель на стенах (богатое дерево, рейки)
PANEL = (74, 50, 32)
for y0 in range(0, 990, 120):
    d.rectangle([0, y0, FW, y0 + 118], fill=PANEL)
    d.line([(0, y0), (FW, y0)], fill=(52, 34, 22), width=6)
    d.line([(0, y0 + 4), (FW, y0 + 4)], fill=(96, 66, 42), width=2)
for x in range(0, FW, 160):
    d.line([(x, 0), (x, 990)], fill=(58, 38, 24), width=3)

# --- пол: паркет + персидский ковёр
d.rectangle([0, 990, FW, FH], fill=(84, 58, 38))
for i in range(-8, 34):
    x = i * 96
    d.line([(x, 990), (x - 300, FH)], fill=(66, 44, 28), width=4)
CARD = (128, 40, 34)
d.rectangle([300, 1020, 2120, FH], fill=CARD)
d.rectangle([340, 1040, 2080, FH], fill=(96, 30, 30))
d.rectangle([340, 1040, 2080, 1090], fill=(30, 60, 96))
d.rectangle([340, 1330, 2080, FH], fill=(24, 54, 86))
d.ellipse([820, 1080, 1620, 1350], fill=(150, 120, 40), outline=(70, 50, 30), width=8)
d.ellipse([940, 1130, 1500, 1310], fill=(120, 34, 32))
d.ellipse([1080, 1170, 1360, 1280], fill=(150, 128, 50))
for _ in range(60):  # узелковый орнамент
    x = random.randint(360, 2060); y = random.randint(1090, 1340)
    d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(210, 190, 120))
d.rectangle([0, 986, FW, 1014], fill=(46, 34, 24))

# --- портьеры у окна (тяжёлый бархат, подхваты)
d.rectangle([560, 60, 1300, 130], fill=(70, 44, 30))     # карниз
for cx0, cx1 in ((575, 760), (1130, 1295)):
    d.rectangle([cx0, 90, cx1, 990], fill=(96, 24, 30))
    for k in range(cx0, cx1, 26):
        d.line([(k, 96), (k, 984)], fill=(70, 16, 22), width=4)
    d.rectangle([cx0 - 10, 84, cx1 + 10, 120], fill=(128, 96, 40))

# --- окно
d.rectangle([740, 180, 1120, 720], fill=(150, 168, 176))
d.rectangle([760, 200, 1100, 700], fill=(202, 218, 228))
d.rectangle([910, 200, 945, 700], fill=(96, 70, 44))
d.rectangle([760, 430, 1100, 462], fill=(96, 70, 44))
d.rectangle([740, 180, 1120, 720], outline=(60, 44, 30), width=16)
d.rectangle([716, 720, 1144, 748], fill=(96, 70, 44))

# --- библиотека слева: шкаф со стеклом, корешки книг
d.rectangle([70, 120, 520, 986], fill=(64, 44, 30))
d.rectangle([92, 150, 498, 620], fill=(40, 34, 32), outline=(132, 104, 54), width=8)
d.rectangle([92, 660, 498, 956], fill=(50, 36, 26), outline=(132, 104, 54), width=8)
for r in range(4):
    for c in range(5):
        col = random.choice([(150, 50, 44), (168, 140, 80), (96, 110, 130),
                             (128, 84, 54), (86, 108, 74)])
        d.rectangle([108 + c * 76, 172 + r * 112, 108 + c * 76 + 58, 268 + r * 112], fill=col)
        d.line([(108 + c * 76 + 58, 172 + r * 112), (108 + c * 76 + 58, 268 + r * 112)],
               fill=(40, 30, 20), width=3)
for c in range(5):
    col = random.choice([(150, 50, 44), (168, 140, 80), (96, 110, 130)])
    d.rectangle([112 + c * 76, 700, 112 + c * 76 + 58, 930], fill=col)

# --- сейф в правом углу
d.rectangle([2060, 620, 2360, 990], fill=(58, 62, 66))
d.rectangle([2080, 648, 2340, 962], fill=(74, 78, 82), outline=(30, 32, 34), width=6)
d.ellipse([2180, 780, 2240, 840], fill=(150, 150, 152), outline=(40, 40, 42), width=5)
d.line([(2210, 810), (2210, 750)], fill=(120, 120, 120), width=8)
d.text((2210, 900), "МОСОБЛГОР", font=f(LATO_B, 15), fill=(150, 150, 150), anchor="ma")

# --- стол: солидный, с зелёным сукном, ящиками
d.rectangle([520, 760, 1840, 1120], fill=(74, 48, 30))
d.rectangle([500, 760, 1860, 820], fill=(102, 70, 42))
d.rectangle([500, 820, 1860, 860], fill=(60, 40, 26))
# ящики (вид спереди)
d.rectangle([540, 900, 1820, 1110], fill=(66, 44, 28))
for i in range(3):
    d.rectangle([560 + i * 420, 918, 960 + i * 420, 1092], fill=(84, 56, 34),
                outline=(46, 32, 20), width=5)
    d.ellipse([748 + i * 420, 990, 796 + i * 420, 1016], fill=(170, 140, 80))
# сукно + бумаги
d.rectangle([860, 830, 1560, 1112], fill=(38, 72, 56))
d.rectangle([900, 856, 1240, 950], fill=(236, 232, 216), outline=(176, 170, 152), width=3)
d.rectangle([980, 900, 1300, 980], fill=(240, 236, 222), outline=(176, 170, 152), width=3)
d.rectangle([1300, 870, 1520, 940], fill=(206, 200, 180))
# письменный прибор + лампа
d.ellipse([1560, 856, 1660, 900], fill=(60, 56, 52))
d.rectangle([1570, 826, 1650, 862], fill=(48, 44, 40))
d.polygon([(1300, 780), (1470, 780), (1510, 700), (1340, 700)], fill=(40, 60, 46),
          outline=(20, 34, 26))
d.rectangle([1382, 780, 1400, 856], fill=(70, 70, 72))
d.ellipse([1360, 850, 1422, 882], fill=(70, 70, 72))

# --- кожаное кресло за столом (спинка с капитоне)
d.rectangle([760, 470, 1180, 780], fill=(74, 30, 26))
d.rounded_rectangle([772, 486, 1168, 770], radius=40, fill=(96, 38, 32),
                    outline=(150, 96, 40), width=6)
for gx in range(820, 1140, 90):
    for gy in range(530, 740, 84):
        d.ellipse([gx - 6, gy - 6, gx + 6, gy + 6], fill=(70, 26, 22))
d.rectangle([600, 620, 792, 792], fill=(74, 30, 26))   # подлокотник
d.rectangle([1160, 620, 1350, 792], fill=(74, 30, 26))

save = add_vignette(im, 0.45)
os.makedirs(OUT, exist_ok=True)
save.save(os.path.join(OUT, "kab_base.png"))
print("base -> assets/mock/cabinet/kab_base.png")


# ============================================================ ПАСХАЛКА 1: дозиметр
def egg_gauge():
    """Дозиметр Р/Ч на стене + стикер «норма» (мем «3,6 Р — не так уж и много»)."""
    ov = layer(); g = ImageDraw.Draw(ov)
    cx, cy, r = 1900, 300, 104
    g.rounded_rectangle([cx - r - 26, cy - r - 30, cx + r + 26, cy + r + 74],
                        radius=18, fill=(206, 200, 178, 255), outline=(58, 54, 46, 255), width=8)
    g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(224, 220, 202, 255),
              outline=(96, 90, 78, 255), width=6)
    for k in range(11):
        a = math.radians(-90 - 60 + 12 * k)
        g.line([(cx + (r - 34) * math.cos(a), cy + (r - 34) * math.sin(a)),
                (cx + (r - 18) * math.cos(a), cy + (r - 18) * math.sin(a))],
               fill=(70, 64, 54, 255), width=3)
    a = math.radians(-90 + 52)
    g.line([(cx, cy), (cx + (r - 30) * math.cos(a), cy + (r - 30) * math.sin(a))],
           fill=(178, 46, 40, 255), width=7)
    g.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(60, 56, 48, 255))
    g.text((cx, cy + 58), "Р/Ч", font=f(LATO_B, 24), fill=(70, 64, 54, 255), anchor="mm")
    g.text((cx, cy + r + 40), "3,6 Р", font=f(GOTHIC, 50), fill=(58, 52, 44, 255), anchor="mm")
    # стикер «норма»
    g.polygon([(cx + 78, cy + 8), (cx + 196, cy - 8), (cx + 206, cy + 92), (cx + 88, cy + 108)],
              fill=(234, 208, 92, 255))
    g.polygon([(cx + 78, cy + 8), (cx + 196, cy - 8), (cx + 206, cy + 92), (cx + 88, cy + 108)],
              outline=(180, 152, 56, 255), width=3)
    g.text((cx + 142, cy + 50), "норма", font=f(LATO_B, 32), fill=(70, 58, 26, 255), anchor="mm")
    return ov


# ============================================================ ПАСХАЛКА 2: план «БЛОК №4»
def egg_block():
    """Чертёжная доска с планом «БЛОК №4» (над столом справа от окна)."""
    ov = layer(); g = ImageDraw.Draw(ov)
    x0, y0, x1, y1 = 1440, 150, 1960, 620
    g.rectangle([x0 - 14, y0 - 14, x1 + 14, y1 + 14], fill=(52, 34, 22, 255))
    g.rectangle([x0, y0, x1, y1], fill=(30, 40, 38, 255), outline=(140, 112, 60, 255), width=8)
    g.text((x0 + 26, y0 + 18), "БЛОК №4", font=f(GOTHIC, 46), fill=(214, 208, 184, 255))
    g.line([(x0 + 26, y0 + 82), (x1 - 26, y0 + 82)], fill=(150, 120, 66, 255), width=3)
    # схематив: секции блока
    g.rectangle([x0 + 40, y0 + 130, x1 - 40, y0 + 300], outline=(190, 186, 168, 255), width=4)
    for k in range(4):
        xx = x0 + 40 + (x1 - x0 - 80) * (k + 1) / 5
        g.line([(xx, y0 + 130), (xx, y0 + 300)], fill=(150, 148, 132, 255), width=3)
    g.ellipse([x0 + 250, y0 + 170, x0 + 350, y0 + 270], outline=(206, 120, 70, 255), width=5)
    g.text((x0 + 300, y0 + 220), "РЕАКТОР", font=f(LATO_B, 17), fill=(206, 150, 110, 255), anchor="mm")
    # выноски/размеры
    g.line([(x0 + 40, y0 + 330), (x1 - 40, y0 + 330)], fill=(150, 148, 132, 255), width=2)
    for i in range(5):
        g.line([(x0 + 46, y0 + 350 + i * 32), (x1 - 70, y0 + 350 + i * 32)],
               fill=(110, 108, 96, 255), width=3)
    g.line([(x0 + 40, y0 + 330), (x0 + 40, y0 + 330)], fill=(190, 186, 168, 255), width=2)
    return ov


EGGS = [("gauge", egg_gauge(), "1", "Дозиметр Р/Ч + стикер «норма»"),
        ("block", egg_block(), "2", "План «БЛОК №4» на доске")]

os.makedirs(OUT, exist_ok=True)
for name, ovl, _, _ in EGGS:
    ovl.save(os.path.join(OUT, "kab_egg_" + name + ".png"))
print("eggs ->", len(EGGS), "files")

# ============================================================ ЛИСТ ПРОВЕРКИ
merged = Image.open(os.path.join(OUT, "kab_base.png")).convert("RGBA")
for name, ovl, _, _ in EGGS:
    merged = Image.alpha_composite(merged, ovl)
merged = merged.convert("RGB")

d = ImageDraw.Draw(merged)
for name, ovl, num, _ in EGGS:
    bb = ovl.getbbox()
    d.rectangle([bb[0] - 6, bb[1] - 6, bb[2] + 6, bb[3] + 6], outline=(232, 64, 52), width=5)
    d.ellipse([bb[0] - 36, bb[1] - 36, bb[0] + 14, bb[1] + 14], fill=(232, 64, 52))
    d.text((bb[0] - 11, bb[1] - 11), num, font=f(GOTHIC, 32), fill=(255, 255, 255), anchor="mm")

INSETS = [("gauge", (1700, 120, 2140, 500)),
          ("block", (1400, 110, 2000, 660))]

W = 2020
sx = W / merged.width
top = merged.resize((W, int(merged.height * sx)), Image.LANCZOS)
TH = 460
tiles = []
for name, box in INSETS:
    crop = merged.crop(box)
    tw = W // len(INSETS) - 8
    tiles.append((name, crop.resize((tw, TH), Image.LANCZOS)))
GAP = 20
H = top.height + GAP + TH + 60 + GAP
sheet = Image.new("RGB", (W, H), (14, 16, 22))
sheet.paste(top, (0, 0))
SheetD = ImageDraw.Draw(sheet)
SheetD.rectangle([0, 0, W, 44], fill=(20, 22, 30))
SheetD.text((14, 8), "Кабинет Старика (КБ) — приличный; пасхалки: дозиметр Р/Ч «норма» + план «БЛОК №4»",
            font=f(LATO_B, 28), fill=(232, 200, 150))
x = 0
names = dict((e[0], e[3]) for e in EGGS)
nums = dict((e[0], e[2]) for e in EGGS)
for name, tile in tiles:
    sheet.paste(tile, (x, top.height + GAP))
    SheetD.rectangle([x, top.height + GAP, x + tile.width, top.height + GAP + TH],
                     outline=(60, 64, 76), width=3)
    SheetD.text((x + 10, top.height + GAP + TH + 8),
                "%s. %s" % (nums[name], names[name]), font=f(LATO_B, 18), fill=(210, 205, 190))
    x += tile.width + 8
os.makedirs(REV, exist_ok=True)
p = os.path.join(REV, "review_79_starik_kabinet.png")
sheet.save(p)
print("sheet ->", os.path.relpath(p, HERE), sheet.size)
