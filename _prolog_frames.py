# -*- coding: utf-8 -*-
"""КАДРЫ ПРОЛОГА — СЛОЯМИ (base + оверлеи).
Правка заказчика 2026-10-11 (вечер): именованные элементы должны ПОЯВЛЯТЬСЯ
в момент произнесения фразы (из темноты), а не висеть весь кадр.
  • base   — фоновый слой кадра (виден всегда);
  • оверлей — элемент(ы), которые аниматик проявляет по фразе (RGBA, прозрачный фон).
Соответствие «оверлей → фраза закадра» задаётся в `_prolog_animatic.py` (REVEALS).
Выход: assets/mock/prolog/s{n}_base.png + s{n}_{label}.png (2400x1350).
"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "mock", "prolog")
GOTHIC = "/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf"
LATO_B = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"

FW, FH = 2400, 1350
GOLD = (226, 186, 104)
CREAM = (246, 238, 222)
RED = (206, 74, 66)
random.seed(7)


def f(p, s):
    return ImageFont.truetype(p, s)


def new_base(top, bot):
    im = Image.new("RGB", (1, FH))
    px = im.load()
    for y in range(FH):
        t = y / (FH - 1)
        px[0, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return im.resize((FW, FH))


def layer():
    return Image.new("RGBA", (FW, FH), (0, 0, 0, 0))


def add_vignette(im, strength=0.75):
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse([-w * 0.22, -h * 0.30, w * 1.22, h * 1.30], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w // 10))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(im, dark, Image.eval(mask, lambda v: 255 - int((255 - v) * strength)))


def person(d, x, y, h, col):
    hh = h * 0.24
    d.ellipse([x - hh / 2, y, x + hh / 2, y + hh], fill=col)
    d.polygon([(x - h * 0.16, y + hh * 1.05), (x + h * 0.16, y + hh * 1.05),
               (x + h * 0.13, y + h), (x - h * 0.13, y + h)], fill=col)


def chronicle_tag(d, txt):
    d.rectangle([70, 70, 70 + 26 + int(len(txt) * 15), 128], fill=(0, 0, 0))
    d.text((90, 82), txt, font=f(LATO_B, 30), fill=(232, 180, 120))


def save_base(im, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    add_vignette(im, 0.75).save(p)
    print("base ", os.path.relpath(p, HERE))


def save_ov(im, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    im.save(p)
    print("ovl  ", os.path.relpath(p, HERE))


# ================================================================ S1 подворотня
im = new_base((16, 20, 34), (6, 8, 16))
d = ImageDraw.Draw(im)
for side, x0 in (("L", 0), ("R", FW - 520)):
    d.rectangle([x0, 0, x0 + 520, FH], fill=(24, 27, 42))
    for by in range(60, FH, 46):
        for bx in range(x0 + ((by // 46) % 2) * 55, x0 + 520, 110):
            d.rectangle([bx + 3, by + 3, bx + 100, by + 38], fill=(30, 34, 52), outline=(20, 23, 36))
d.ellipse([820, 980, 1600, 1180], fill=(24, 30, 46))
person(d, 1180, 700, 300, (7, 8, 14))
person(d, 1250, 720, 270, (9, 10, 16))
for _ in range(220):
    x = random.randint(0, FW); y = random.randint(0, FH)
    d.line([(x, y), (x - 6, y + 40)], fill=(60, 70, 95), width=2)
chronicle_tag(d, "ХРОНИКА · 2061")
save_base(im, "s1_base.png")

ov = layer(); d = ImageDraw.Draw(ov)
d.rectangle([560, 250, 1180, 520], fill=(18, 20, 30, 255), outline=(70, 74, 96, 255), width=4)
d.text((870, 300), "МАРС", font=f(GOTHIC, 96), fill=(210, 196, 160, 255), anchor="ma")
d.text((870, 410), "ДЕЛО ОБЩЕЕ?", font=f(GOTHIC, 62), fill=(200, 150, 90, 255), anchor="ma")
d.line([(600, 470), (1140, 470)], fill=(150, 70, 60, 255), width=10)
save_ov(ov, "s1_poster.png")

# ================================================================ S2 космодром (ракета)
im = new_base((26, 34, 62), (10, 13, 24))
d = ImageDraw.Draw(im)
d.ellipse([1560, 780, 2320, 1260], fill=(66, 58, 74))
d.rectangle([0, 1120, FW, FH], fill=(14, 16, 24))
cx = 820
d.polygon([(cx - 96, 1120), (cx - 62, 470), (cx, 250), (cx + 62, 470), (cx + 96, 1120)], fill=(208, 212, 222))
d.polygon([(cx, 250), (cx + 62, 470), (cx, 430)], fill=(150, 156, 168))
for yy, ww, col in ((520, 60, RED), (720, 66, (198, 202, 214)), (900, 72, (198, 202, 214)), (1040, 78, (198, 202, 214))):
    d.rectangle([cx - ww, yy, cx + ww, yy + 58], fill=col)
for sx in (cx - 150, cx + 150):
    d.polygon([(sx - 34, 1120), (sx - 30, 560), (sx, 470), (sx + 30, 560), (sx + 34, 1120)], fill=(188, 192, 204))
    d.rectangle([sx - 30, 560, sx + 30, 640], fill=RED)
d.rectangle([cx - 210, 1090, cx + 210, 1130], fill=(40, 44, 58))
d.rectangle([cx + 210, 360, cx + 256, 1120], fill=(60, 66, 84))
for gy in range(420, 1100, 90):
    d.line([(cx + 256, gy), (cx + 104, gy + 30)], fill=(92, 98, 118), width=6)
for i, (x, w, h) in enumerate(((1500, 480, 210), (2040, 420, 170), (560, 260, 130))):
    col = (56, 64, 90) if i % 2 == 0 else (46, 54, 78)
    d.rectangle([x, 1120 - h, x + w, 1120], fill=col)
    d.rectangle([x, 1120 - h, x + w, 1120 - h + 24], fill=(80, 90, 120))
for x in (380, 1360, 1960):
    d.line([(x, 1120), (x - 34, 900)], fill=(120, 126, 150), width=4)
    d.ellipse([x - 64, 840, x + 4, 908], fill=(126, 132, 154))
for x in range(1180, 2360, 160):
    person(d, x, 1010, 120, (10, 12, 20))
chronicle_tag(d, "КОСМОДРОМ · 2061")
save_base(im, "s2_base.png")

# ================================================================ S3 вопрос
im = new_base((22, 26, 42), (8, 9, 16))
d = ImageDraw.Draw(im)
for x in range(160, 2320, 130):
    person(d, x, 1080, 190 + (x // 130 % 3) * 30, (9, 10, 16))
chronicle_tag(d, "ЗАЛ · ВОПРОС")
save_base(im, "s3_base.png")

ov = layer(); d = ImageDraw.Draw(ov)
d.rectangle([340, 250, 2060, 950], fill=(12, 16, 26, 255), outline=(80, 120, 175, 255), width=6)
d.text((1200, 330), "«МАРС —", font=f(GOTHIC, 120), fill=CREAM + (255,), anchor="ma")
d.text((1200, 480), "ДЕЛО ОБЩЕЕ?»", font=f(GOTHIC, 120), fill=GOLD + (255,), anchor="ma")
save_ov(ov, "s3_q1.png")

ov = layer(); d = ImageDraw.Draw(ov)
d.text((1200, 680), "«ОБЩЕЕ!»", font=f(GOTHIC, 96), fill=(150, 210, 150, 255), anchor="ma")
save_ov(ov, "s3_q2.png")

ov = layer(); d = ImageDraw.Draw(ov)
d.text((1200, 820), "А ЧТО ЖЕ ОБЫЧНЫХ ЛЮДЕЙ НЕТ?", font=f(GOTHIC, 54), fill=(206, 211, 230, 255), anchor="ma")
save_ov(ov, "s3_q3.png")

# ================================================================ S4 ролик-нарезка
im = new_base((10, 12, 22), (4, 5, 10))
d = ImageDraw.Draw(im)
chronicle_tag(d, "ВИДЕОРОЛИК · НАРЕЗКА")
save_base(im, "s4_base.png")

ov = layer(); d = ImageDraw.Draw(ov)
d.rectangle([420, 230, 1980, 1120], fill=(8, 20, 34, 255), outline=(120, 124, 140, 255), width=5)
for _ in range(120):
    x = random.randint(450, 1950); y = random.randint(260, 1000)
    d.point((x, y), fill=(200, 210, 235, 255))
d.ellipse([1500, 780, 1900, 1110], fill=(176, 118, 88, 255))
d.ellipse([1500, 780, 1900, 1110], outline=(220, 180, 150, 255))
d.polygon([(1080, 520), (1080, 840), (1420, 680)], fill=(235, 235, 238, 255))
for _ in range(24):
    y = random.randint(240, 1110)
    d.rectangle([420, y, 1980, y + random.randint(2, 7)], fill=(40, 120, 150, 255))
save_ov(ov, "s4_video.png")

ov = layer(); d = ImageDraw.Draw(ov)
d.rectangle([560, 900, 1840, 1010], fill=(0, 0, 0, 255))
d.text((1200, 922), "А ЧТО ЖЕ ОБЫЧНЫХ ЛЮДЕЙ НЕТ?", font=f(GOTHIC, 44), fill=(230, 190, 120, 255), anchor="ma")
save_ov(ov, "s4_q.png")

# ================================================================ S5 лозунг облетел страну
im = new_base((30, 26, 40), (12, 10, 18))
d = ImageDraw.Draw(im)
d.polygon([(360, 470), (980, 330), (1500, 470), (1480, 900), (900, 1010), (420, 880)],
          fill=(38, 52, 72), outline=(90, 110, 140))
chronicle_tag(d, "ЛОЗУНГ · СТРАНА")
save_base(im, "s5_base.png")

ov = layer(); d = ImageDraw.Draw(ov)
for x, y in ((560, 520), (860, 470), (1120, 560), (720, 720), (1040, 760)):
    d.rectangle([x, y, x + 230, y + 130], fill=(186, 62, 54, 255))
    d.text((x + 115, y + 40), "МАРС —", font=f(GOTHIC, 34), fill=CREAM + (255,), anchor="ma")
    d.text((x + 115, y + 82), "ДЛЯ ВСЕХ!", font=f(GOTHIC, 30), fill=CREAM + (255,), anchor="ma")
save_ov(ov, "s5_posters.png")

ov = layer(); d = ImageDraw.Draw(ov)
d.rectangle([1720, 620, 2300, 1120], fill=(64, 60, 70, 255))
for x in range(1760, 2280, 90):
    d.rectangle([x, 700, x + 46, 1120], fill=(90, 86, 96, 255))
d.polygon([(1700, 620), (2320, 620), (2010, 520)], fill=(76, 70, 82, 255))
d.text((2010, 1160), "ВЕРХОВНЫЙ СОВЕТ", font=f(LATO_B, 40), fill=(230, 190, 120, 255), anchor="ma")
save_ov(ov, "s5_soviet.png")

ov = layer(); d = ImageDraw.Draw(ov)
d.text((760, 1160), "2 МЕСТА «С УЛИЦЫ»", font=f(GOTHIC, 52), fill=(255, 210, 120, 255), anchor="ma")
save_ov(ov, "s5_seats.png")

# ================================================================ S6 очередь
im = new_base((34, 32, 44), (14, 13, 20))
d = ImageDraw.Draw(im)
d.rectangle([1500, 380, 2380, 1120], fill=(60, 54, 46))
d.rectangle([1500, 380, 2380, 470], fill=(76, 68, 56))
d.text((1940, 520), "ПРИЁМНАЯ", font=f(GOTHIC, 64), fill=GOLD, anchor="ma")
d.rectangle([1660, 720, 1840, 1120], fill=(30, 26, 20))
d.rectangle([2000, 720, 2180, 1120], fill=(30, 26, 20))
x, i = 240, 0
while x < 1460:
    h = 300 + (i % 3) * 60
    person(d, x + 90, 820, h, (12, 13, 20))
    x += 150
    i += 1
chronicle_tag(d, "ОЧЕРЕДЬ · ПРИЁМНАЯ")
save_base(im, "s6_base.png")

print("готово: base + оверлеи")
