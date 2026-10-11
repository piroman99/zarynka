# -*- coding: utf-8 -*-
"""Раскадровка вариантов интро-медальона (3 концепта x 4 кадра).
Запуск: python3 _medallion_board.py   (из каталога novella/zaryanka)
Выход:  assets/review/review_25_medallion.png
"""
import os, random, math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "assets", "gen", "logo_b_0.jpg")
OUT = os.path.join(HERE, "assets", "review", "review_25_medallion.png")

BG = (13, 17, 23)
TILE_W, TILE_H = 420, 236
CAP_H = 58
PAD, GAP = 26, 14
ROWS = 3
W = PAD * 2 + TILE_W * 4 + GAP * 3
H = PAD * 2 + 40 + ROWS * (TILE_H + CAP_H) + GAP * (ROWS - 1)


def F(sz, bold=False):
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for root in ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu"]:
        for n in names:
            p = os.path.join(root, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


med = Image.open(LOGO).convert("RGBA").resize((300, 300))
_mask = Image.new("L", (300, 300), 0)
ImageDraw.Draw(_mask).ellipse((7, 7, 293, 293), fill=255)
med.putalpha(_mask)


def with_alpha(im, a):
    r, g, b, al = im.split()
    al = al.point(lambda v: int(v * a / 255))
    return Image.merge("RGBA", (r, g, b, al))


def transform(scale, rot, alpha, bright=1.0):
    m = ImageEnhance.Brightness(med).enhance(bright)
    if rot:
        m = m.rotate(rot, resample=Image.BICUBIC, expand=False)
    if scale != 1.0:
        s = max(8, int(300 * scale))
        m = m.resize((s, s), Image.LANCZOS)
    return with_alpha(m, alpha)


def radial(tile):
    d = ImageDraw.Draw(tile)
    cx, cy = TILE_W // 2, TILE_H // 2
    for i in range(28, 0, -1):
        t = i / 28.0
        rr = int(t * 320)
        c = int(6 + (1 - t) * 14)
        d.ellipse((cx - rr, cy - int(rr * 0.6), cx + rr, cy + int(rr * 0.6)),
                  fill=(c, c + 3, c + 8))


def sparks(tile, n, spread=120, alpha=255, r=(1, 3)):
    d = ImageDraw.Draw(tile)
    cx, cy = TILE_W // 2, TILE_H // 2
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi)
        rad = random.uniform(10, spread)
        x = cx + math.cos(a) * rad
        y = cy + math.sin(a) * rad * 0.7
        rr = random.randint(r[0], r[1])
        col = random.choice([(255, 226, 160), (255, 170, 120), (255, 255, 240)])
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + (alpha,))


def paste_center(tile, im):
    x = (TILE_W - im.width) // 2
    y = (TILE_H - im.height) // 2
    tile.alpha_composite(im, (x, y))


def starfield(tile, n=60):
    d = ImageDraw.Draw(tile)
    for _ in range(n):
        x = random.randint(0, TILE_W)
        y = random.randint(0, TILE_H)
        rr = random.choice([1, 1, 1, 2])
        v = random.randint(160, 255)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(v, v, v, 255))


def tile_k1(step):
    t = Image.new("RGBA", (TILE_W, TILE_H), (0, 0, 0, 0))
    radial(t)
    if step == 0:
        paste_center(t, transform(1.00, 0, 255))
    elif step == 1:
        paste_center(t, transform(1.03, 4, 255, bright=1.25))
        sparks(t, 14, spread=70, r=(1, 2))
    elif step == 2:
        paste_center(t, transform(0.88, 14, 150, bright=1.4))
        sparks(t, 40, spread=110)
    else:
        paste_center(t, transform(0.80, 22, 40))
        sparks(t, 90, spread=150, r=(1, 2))
    return t


def tile_k2(step):
    t = Image.new("RGBA", (TILE_W, TILE_H), (0, 0, 0, 0))
    radial(t)
    if step == 0:
        paste_center(t, transform(1.00, 0, 255))
    elif step == 1:
        paste_center(t, transform(1.35, 0, 255))
    elif step == 2:
        paste_center(t, transform(1.9, 0, 255))
        starfield(t, 40)
        ImageDraw.Draw(t).ellipse((40, TILE_H // 2 - 90, TILE_W - 40, TILE_H // 2 + 90),
                                  outline=(255, 226, 160, 200), width=3)
    else:
        starfield(t, 80)
        d = ImageDraw.Draw(t)
        d.ellipse((TILE_W - 150, TILE_H - 120, TILE_W - 40, TILE_H - 30),
                  fill=(190, 90, 60, 255))
        d.ellipse((TILE_W - 150, TILE_H - 120, TILE_W - 40, TILE_H - 30),
                  outline=(255, 200, 150, 180), width=2)
    return t


def tile_k3(step):
    t = Image.new("RGBA", (TILE_W, TILE_H), (0, 0, 0, 0))
    radial(t)
    if step == 0:
        paste_center(t, transform(1.00, 0, 255))
    elif step == 1:
        paste_center(t, transform(0.82, 55, 255))
    elif step == 2:
        paste_center(t, transform(0.5, 120, 220))
    else:
        d = ImageDraw.Draw(t)
        cx, cy = TILE_W // 2, TILE_H // 2
        for rr, col in [(10, (255, 240, 200)), (5, (255, 255, 255))]:
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col + (255,))
        starfield(t, 40)
    return t


CONCEPTS = [
    ("К1  птица улетает + медальон растворяется  ★", tile_k1,
     ["0–1 с  дыхание", "1–2 с  вспышка, птица бьёт крыльями",
      "2–3.5 с  птица улетает, металл тает", "3.5–4.5 с  искры гаснут"]),
    ("К2  медальон-иллюминатор", tile_k2,
     ["0–1 с  значок в темноте", "1–2 с  зум внутрь",
      "2–3 с  обод = иллюминатор", "3–4 с  звёзды → Марс"]),
    ("К3  подброс монеты", tile_k3,
     ["0–1 с  значок в темноте", "1–2 с  подброс, вращение",
      "2–3 с  улетает в глубину", "3–4 с  становится звездой"]),
]

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((PAD, PAD), "«Зарянка» — интро-медальон: 3 концепта (раскадровка)",
       font=F(24, True), fill=(240, 240, 245))

random.seed(7)
y0 = PAD + 40
for r, (title, fn, caps) in enumerate(CONCEPTS):
    y = y0 + r * (TILE_H + CAP_H + GAP)
    d.text((PAD, y), title, font=F(17, True), fill=(255, 210, 130))
    ty = y + 24
    for c in range(4):
        x = PAD + c * (TILE_W + GAP)
        t = fn(c)
        img.paste(t, (x, ty), t)
        d.rectangle((x, ty, x + TILE_W - 1, ty + TILE_H - 1), outline=(60, 66, 80))
        d.text((x + 4, ty + TILE_H + 6), caps[c], font=F(13), fill=(200, 205, 215))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT)
print("saved", OUT, img.size)
