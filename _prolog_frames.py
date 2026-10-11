# -*- coding: utf-8 -*-
"""ЧЕРНОВЫЕ КАДРЫ ПРОЛОГА (кадры-моки, 0 ₽, PIL).
Кадр = схематичная иллюстрация сцены в тоне будущего финала (хроника-пролог).
Стиль: тёмный кинематографичный мок — силуэты, плакаты, ракета, толпа.
Выход: assets/mock/prolog/s1..s6.png (2400x1350, с запасом под кен-бёрнс).
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "mock", "prolog")
GOTHIC = "/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf"
LATO = "/usr/share/fonts/truetype/lato/Lato-Medium.ttf"
LATO_B = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"

FW, FH = 2400, 1350
GOLD = (226, 186, 104)
CREAM = (246, 238, 222)
RED = (206, 74, 66)
random.seed(7)


def f(p, s):
    return ImageFont.truetype(p, s)


def vgrad(size, top, bot):
    w, h = size
    im = Image.new("RGB", (1, h))
    px = im.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return im.resize((w, h))


def add_vignette(im, strength=0.8):
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse([-w * 0.22, -h * 0.30, w * 1.22, h * 1.30], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w // 10))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(im, dark, Image.eval(mask, lambda v: 255 - int((255 - v) * strength)))


def add_grain(im, amt=16):
    w, h = im.size
    n = Image.effect_noise((w, h), amt).convert("L")
    return Image.blend(im, Image.merge("RGB", (n, n, n)), 0.10)


def person(d, x, y, h, col):
    """силуэт человека: голова + тело."""
    hh = h * 0.24
    d.ellipse([x - hh / 2, y, x + hh / 2, y + hh], fill=col)
    d.polygon([(x - h * 0.16, y + hh * 1.05), (x + h * 0.16, y + hh * 1.05),
               (x + h * 0.13, y + h), (x - h * 0.13, y + h)], fill=col)


def chronicle_tag(d, txt):
    d.rectangle([70, 70, 70 + 26 + int(len(txt) * 15), 128], fill=(0, 0, 0))
    d.text((90, 82), txt, font=f(LATO_B, 30), fill=(232, 180, 120))


def save(im, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    add_grain(add_vignette(im, 0.75), 14).save(p)
    print("saved", os.path.relpath(p, HERE), im.size)


# ---------------------------------------------------------------- S1 подворотня
im = vgrad((FW, FH), (16, 20, 34), (6, 8, 16))
d = ImageDraw.Draw(im)
# стены кирпичом
for side, x0 in (("L", 0), ("R", FW - 520)):
    d.rectangle([x0, 0, x0 + 520, FH], fill=(24, 27, 42))
    for by in range(60, FH, 46):
        for bx in range(x0 + ((by // 46) % 2) * 55, x0 + 520, 110):
            d.rectangle([bx + 3, by + 3, bx + 100, by + 38], fill=(30, 34, 52), outline=(20, 23, 36))
# лужа-свет
d.ellipse([820, 980, 1600, 1180], fill=(24, 30, 46))
# силуэт у стены
person(d, 1180, 700, 300, (7, 8, 14))
person(d, 1250, 720, 270, (9, 10, 16))
# плакат-вопрос
d.rectangle([560, 250, 1180, 520], fill=(18, 20, 30), outline=(70, 74, 96), width=4)
d.text((870, 300), "МАРС", font=f(GOTHIC, 96), fill=(210, 196, 160), anchor="ma")
d.text((870, 410), "ДЕЛО ОБЩЕЕ?", font=f(GOTHIC, 62), fill=(200, 150, 90), anchor="ma")
d.line([(600, 470), (1140, 470)], fill=(150, 70, 60), width=10)   # зачёркнуто
# дождь
for _ in range(220):
    x = random.randint(0, FW); y = random.randint(0, FH)
    d.line([(x, y), (x - 6, y + 40)], fill=(60, 70, 95), width=2)
chronicle_tag(d, "ХРОНИКА · 2061")
save(im, "s1.png")

# ---------------------------------------------------------------- S2 КОСМОДРОМ (ракета)
# Правка заказчика 2026-10-11: РАКЕТЫ ВОЗВРАЩАЕМ — «ракеты красиво и понятно».
# В прологе это космодром (Байконур), а Звёздный городок (ЦПК) — отдельной врезкой ПОЗЖЕ.
im = vgrad((FW, FH), (26, 34, 62), (10, 13, 24))
d = ImageDraw.Draw(im)
# предрассветное зарево у горизонта
d.ellipse([1560, 780, 2320, 1260], fill=(66, 58, 74))
d.rectangle([0, 1120, FW, FH], fill=(14, 16, 24))   # земля/бетон
# --- ракета ------------------------------------------------
cx = 820
d.polygon([(cx - 96, 1120), (cx - 62, 470), (cx, 250), (cx + 62, 470), (cx + 96, 1120)],
          fill=(208, 212, 222))
d.polygon([(cx, 250), (cx + 62, 470), (cx, 430)], fill=(150, 156, 168))
# ступени и красные пояса
for yy, ww, col in ((520, 60, RED), (720, 66, (198, 202, 214)), (900, 72, (198, 202, 214)), (1040, 78, (198, 202, 214))):
    d.rectangle([cx - ww, yy, cx + ww, yy + 58], fill=col)
# боковые блоки (пакеты первой ступени)
for sx in (cx - 150, cx + 150):
    d.polygon([(sx - 34, 1120), (sx - 30, 560), (sx, 470), (sx + 30, 560), (sx + 34, 1120)],
              fill=(188, 192, 204))
    d.rectangle([sx - 30, 560, sx + 30, 640], fill=RED)
# стартовый стол + кабель-мачта
d.rectangle([cx - 210, 1090, cx + 210, 1130], fill=(40, 44, 58))
d.rectangle([cx + 210, 360, cx + 256, 1120], fill=(60, 66, 84))
for gy in range(420, 1100, 90):
    d.line([(cx + 256, gy), (cx + 104, gy + 30)], fill=(92, 98, 118), width=6)
# --- модули/ангары справа ---------------------------------
for i, (x, w, h) in enumerate(((1500, 480, 210), (2040, 420, 170), (560, 260, 130))):
    col = (56, 64, 90) if i % 2 == 0 else (46, 54, 78)
    d.rectangle([x, 1120 - h, x + w, 1120], fill=col)
    d.rectangle([x, 1120 - h, x + w, 1120 - h + 24], fill=(80, 90, 120))
# --- прожекторы-мачты --------------------------------------
for x in (380, 1360, 1960):
    d.line([(x, 1120), (x - 34, 900)], fill=(120, 126, 150), width=4)
    d.ellipse([x - 64, 840, x + 4, 908], fill=(126, 132, 154))
# --- люди для масштаба -------------------------------------
for x in range(1180, 2360, 160):
    person(d, x, 1010, 120, (10, 12, 20))
chronicle_tag(d, "КОСМОДРОМ · 2061")
save(im, "s2.png")

# ---------------------------------------------------------------- S3 вопрос
im = vgrad((FW, FH), (22, 26, 42), (8, 9, 16))
d = ImageDraw.Draw(im)
d.rectangle([340, 250, 2060, 950], fill=(12, 16, 26), outline=(80, 120, 175), width=6)
d.text((1200, 330), "«МАРС —", font=f(GOTHIC, 120), fill=CREAM, anchor="ma")
d.text((1200, 480), "ДЕЛО ОБЩЕЕ?»", font=f(GOTHIC, 120), fill=GOLD, anchor="ma")
d.text((1200, 680), "«ОБЩЕЕ!»", font=f(GOTHIC, 96), fill=(150, 210, 150), anchor="ma")
d.text((1200, 820), "А ЧТО ЖЕ ОБЫЧНЫХ ЛЮДЕЙ НЕТ?", font=f(GOTHIC, 54), fill=(200, 205, 225), anchor="ma")
# хор толпы
for x in range(160, 2320, 130):
    person(d, x, 1080, 190 + (x // 130 % 3) * 30, (9, 10, 16))
chronicle_tag(d, "ЗАЛ · ВОПРОС")
save(im, "s3.png")

# ---------------------------------------------------------------- S4 ролик-нарезка
im = vgrad((FW, FH), (10, 12, 22), (4, 5, 10))
d = ImageDraw.Draw(im)
d.rectangle([420, 230, 1980, 1120], fill=(8, 20, 34), outline=(120, 124, 140), width=5)
# звёзды внутри
for _ in range(120):
    x = random.randint(450, 1950); y = random.randint(260, 1000)
    d.point((x, y), fill=(200, 210, 235))
# планета
d.ellipse([1500, 780, 1900, 1110], fill=(176, 118, 88))
d.ellipse([1500, 780, 1900, 1110], outline=(220, 180, 150))
# play
d.polygon([(1080, 520), (1080, 840), (1420, 680)], fill=(235, 235, 238))
# глитч-полосы
for _ in range(24):
    y = random.randint(240, 1110)
    d.rectangle([420, y, 1980, y + random.randint(2, 7)], fill=(40, 120, 150))
# неудобный вопрос в конце
d.rectangle([560, 900, 1840, 1010], fill=(0, 0, 0))
d.text((1200, 922), "А ЧТО ЖЕ ОБЫЧНЫХ ЛЮДЕЙ НЕТ?", font=f(GOTHIC, 44), fill=(230, 190, 120), anchor="ma")
chronicle_tag(d, "ВИДЕОРОЛИК · НАРЕЗКА")
save(im, "s4.png")

# ---------------------------------------------------------------- S5 лозунг облетел страну
im = vgrad((FW, FH), (30, 26, 40), (12, 10, 18))
d = ImageDraw.Draw(im)
# силуэт карты
d.polygon([(360, 470), (980, 330), (1500, 470), (1480, 900), (900, 1010), (420, 880)],
          fill=(38, 52, 72), outline=(90, 110, 140))
# красные плакаты-лозунги
for x, y in ((560, 520), (860, 470), (1120, 560), (720, 720), (1040, 760)):
    d.rectangle([x, y, x + 230, y + 130], fill=(186, 62, 54))
    d.text((x + 115, y + 40), "МАРС —", font=f(GOTHIC, 34), fill=CREAM, anchor="ma")
    d.text((x + 115, y + 82), "ДЛЯ ВСЕХ!", font=f(GOTHIC, 30), fill=CREAM, anchor="ma")
# здание Верховного Совета
d.rectangle([1720, 620, 2300, 1120], fill=(64, 60, 70))
for x in range(1760, 2280, 90):
    d.rectangle([x, 700, x + 46, 1120], fill=(90, 86, 96))
d.polygon([(1700, 620), (2320, 620), (2010, 520)], fill=(76, 70, 82))
d.text((2010, 1160), "ВЕРХОВНЫЙ СОВЕТ", font=f(LATO_B, 40), fill=(230, 190, 120), anchor="ma")
d.text((760, 1160), "2 МЕСТА «С УЛИЦЫ»", font=f(GOTHIC, 52), fill=(255, 210, 120), anchor="ma")
chronicle_tag(d, "ЛОЗУНГ · СТРАНА")
save(im, "s5.png")

# ---------------------------------------------------------------- S6 очередь
im = vgrad((FW, FH), (34, 32, 44), (14, 13, 20))
d = ImageDraw.Draw(im)
# здание приёмной
d.rectangle([1500, 380, 2380, 1120], fill=(60, 54, 46))
d.rectangle([1500, 380, 2380, 470], fill=(76, 68, 56))
d.text((1940, 520), "ПРИЁМНАЯ", font=f(GOTHIC, 64), fill=GOLD, anchor="ma")
d.rectangle([1660, 720, 1840, 1120], fill=(30, 26, 20))
d.rectangle([2000, 720, 2180, 1120], fill=(30, 26, 20))
# очередь силуэтов
x = 240
i = 0
while x < 1460:
    h = 300 + (i % 3) * 60
    person(d, x + 90, 820 - h + h, h, (12, 13, 20))
    x += 150
    i += 1
chronicle_tag(d, "ОЧЕРЕДЬ · ПРИЁМНАЯ")
save(im, "s6.png")

print("готово: 6 кадров-моков")
