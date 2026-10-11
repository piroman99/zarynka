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


# ================================================================ S1 подворотня (СОВЕТСКАЯ)
# Правка заказчика 2026-10-11: «слишком западная подворотня; советская — другая, менее аккуратная».
# Советский двор-подворотня: облупленная кирпичная стена, ржавая водосточная труба, арка во двор,
# тусклая лампочка на проводе, мусорные контейнеры, лужа и люк на асфальте.
im = new_base((14, 17, 28), (5, 7, 14))
d = ImageDraw.Draw(im)

# --- левая кирпичная стена, облупленная
d.rectangle([0, 0, 560, 1120], fill=(26, 28, 42))
for by in range(30, 1120, 44):
    for bx in range(((by // 44) % 2) * 52, 560, 104):
        d.rectangle([bx + 2, by + 2, bx + 98, by + 38], fill=(31, 34, 50), outline=(19, 21, 34))
for _ in range(28):
    x = random.randint(10, 470); y = random.randint(40, 1050)
    d.rectangle([x, y, x + random.randint(30, 120), y + random.randint(20, 70)],
                fill=random.choice([(38, 40, 56), (16, 18, 28), (24, 26, 40)]))
for _ in range(12):
    x = random.randint(20, 520)
    d.line([(x, 60), (x + random.randint(-10, 10), random.randint(400, 900))], fill=(15, 17, 26), width=2)

# --- дальняя стена двора (глубь)
d.rectangle([560, 360, 1400, 1120], fill=(20, 22, 34))
for _ in range(26):
    x = random.randint(580, 1340); y = random.randint(390, 1080)
    d.rectangle([x, y, x + random.randint(20, 90), y + random.randint(16, 52)],
                fill=random.choice([(16, 18, 28), (26, 28, 42)]))
d.rectangle([980, 660, 1120, 800], fill=(13, 15, 24), outline=(42, 44, 60), width=4)
d.rectangle([998, 678, 1102, 782], fill=(46, 44, 36))

# --- здание справа с АРКОЙ во двор
d.rectangle([1400, 280, FW, 1120], fill=(23, 25, 38))
for by in range(300, 1120, 46):
    for bx in range(1400 + ((by // 46) % 2) * 56, FW, 112):
        d.rectangle([bx + 2, by + 2, bx + 106, by + 40], fill=(28, 31, 46), outline=(18, 20, 32))
d.pieslice([1520, 380, 2120, 760], 180, 360, fill=(58, 60, 78))
d.rectangle([1520, 570, 2120, 1120], fill=(58, 60, 78))
d.pieslice([1570, 430, 2070, 720], 180, 360, fill=(30, 36, 54))
d.rectangle([1570, 575, 2070, 1120], fill=(30, 36, 54))
d.ellipse([1740, 700, 1880, 810], fill=(70, 74, 96))
d.ellipse([1760, 715, 1780, 735], fill=(152, 142, 112))
for x in (1660, 1720, 1900, 1960):
    person(d, x, 980, 150, (16, 18, 28))

# --- асфальт, лужа, люк
d.rectangle([0, 1120, FW, FH], fill=(18, 20, 30))
for _ in range(18):
    x = random.randint(0, FW); y = random.randint(1130, 1340)
    d.line([(x, y), (x + random.randint(-60, 60), y + random.randint(-14, 14))], fill=(38, 42, 56), width=2)
d.ellipse([700, 1180, 1560, 1330], fill=(24, 30, 44))
d.ellipse([820, 1210, 1180, 1270], fill=(38, 46, 64))
d.ellipse([1660, 1180, 1860, 1300], fill=(30, 32, 44), outline=(52, 56, 72), width=4)

# --- ржавая водосточная труба
d.rectangle([472, 0, 502, 1120], fill=(56, 50, 48))
for yy in range(120, 1100, 220):
    d.rectangle([466, yy, 508, yy + 16], fill=(40, 36, 36))
for _ in range(20):
    y = random.randint(40, 1080)
    d.line([(480, y), (480, y + random.randint(20, 70))], fill=(92, 62, 44), width=2)

# --- мусорные контейнеры
for cx, col in ((1180, (44, 50, 60)), (1360, (40, 46, 56))):
    d.rectangle([cx, 990, cx + 200, 1118], fill=col)
    d.rectangle([cx - 6, 970, cx + 206, 1000], fill=(56, 62, 74))
d.rectangle([1210, 1010, 1250, 1040], fill=(70, 76, 90))

# --- лампочка на проводе
x0, y0, x1, y1 = 560, 150, 1400, 200
for i in range(0, 61):
    t = i / 60
    x = x0 + (x1 - x0) * t
    y = y0 + (y1 - y0) * t + 90 * (4 * t * (1 - t))
    d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(60, 62, 78))
bx = 980; by = y0 + (y1 - y0) * 0.5 + 90
d.line([(bx, by), (bx, by + 34)], fill=(60, 62, 78), width=3)
d.ellipse([bx - 16, by + 30, bx + 16, by + 66], fill=(210, 200, 160))
d.ellipse([bx - 62, by - 30, bx + 62, by + 98], fill=(60, 56, 42))

# --- силуэты у стены (с кепками)
for px, ph, col in ((980, 320, (8, 9, 15)), (1080, 286, (10, 11, 17))):
    person(d, px, 760, ph, col)
    d.rectangle([px - ph * 0.20, 760 + ph * 0.02, px + ph * 0.20, 760 + ph * 0.10], fill=col)

# --- ПАСХАЛКА: котобус — детский рисунок МЕЛОМ на кирпичной стене (псевдоним автора → Catbus)
CK = (210, 205, 190)
kx0, ky0, kx1, ky1 = 165, 815, 470, 955
d.rounded_rectangle([kx0, ky0, kx1, ky1], radius=42, outline=CK, width=5)
d.polygon([(kx0 + 60, ky0 + 6), (kx0 + 108, ky0 - 54), (kx0 + 150, ky0 + 6)], outline=CK, width=5)
d.polygon([(kx1 - 150, ky0 + 6), (kx1 - 108, ky0 - 54), (kx1 - 60, ky0 + 6)], outline=CK, width=5)
for wx in range(kx0 + 46, kx1 - 40, 74):
    d.rectangle([wx, ky0 + 34, wx + 46, ky0 + 86], outline=CK, width=4)
for lx in range(kx0 + 34, kx1 - 30, 62):
    d.line([(lx, ky1), (lx, ky1 + 58)], fill=CK, width=5)
d.line([(kx1 - 4, ky0 + 96), (kx1 + 66, ky0 + 70), (kx1 + 74, ky0 + 128)], fill=CK, width=5)
d.ellipse([kx1 - 96, ky0 + 40, kx1 - 78, ky0 + 58], outline=CK, width=4)
for k in range(3):
    d.line([(kx1 - 96, ky0 + 74 + k * 12), (kx1 - 10, ky0 + 62 + k * 16)], fill=CK, width=2)

# --- редкая морось
for _ in range(120):
    x = random.randint(0, FW); y = random.randint(0, FH)
    d.line([(x, y), (x - 5, y + 34)], fill=(52, 60, 80), width=2)
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
# --- ПАСХАЛКА: современный транспорт-2061 с маршрутом «410» на краю космодрома
tx0, ty0, tx1, ty1 = 120, 986, 486, 1098
d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=34, fill=(172, 180, 196), outline=(96, 104, 122), width=3)
d.rounded_rectangle([tx0 + 6, ty0 + 6, tx1 - 6, ty0 + 40], radius=24, fill=(198, 205, 220))
d.rounded_rectangle([tx0 + 34, ty0 + 40, tx1 - 30, ty0 + 78], radius=14, fill=(22, 30, 42))
d.rounded_rectangle([tx0 + 40, ty0 + 45, tx1 - 36, ty0 + 55], radius=8, fill=(60, 78, 100))
d.rounded_rectangle([tx0 + 12, ty0 + 12, tx0 + 96, ty0 + 44], radius=8, fill=(12, 14, 20))
d.text((tx0 + 20, ty0 + 14), "410", font=f(GOTHIC, 26), fill=(120, 234, 210))
d.rounded_rectangle([tx1 - 40, ty0 + 18, tx1 - 10, ty0 + 40], radius=6, fill=(246, 232, 180))
d.line([(tx0 + 20, ty1 - 26), (tx1 - 20, ty1 - 26)], fill=(120, 234, 210), width=3)
d.rounded_rectangle([tx0 + 10, ty1 - 14, tx1 - 10, ty1], radius=6, fill=(60, 66, 80))
for cx in (tx0 + 78, tx1 - 78):
    d.ellipse([cx - 30, ty1 - 26, cx + 30, ty1 + 18], fill=(30, 32, 40))
    d.ellipse([cx - 16, ty1 - 12, cx + 16, ty1 + 4], fill=(120, 126, 140))
d.line([(tx0 + 30, ty0 + 20), (tx0 + 150, ty0 + 12)], fill=(200, 205, 215), width=4)
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
# --- ПАСХАЛКА: цифровые часы 06:07 на стене (валидное время, но читается «шесть-семь»)
clx0, cly0, clx1, cly1 = 1552, 536, 1772, 614
d.rounded_rectangle([clx0, cly0, clx1, cly1], radius=8, fill=(16, 18, 20), outline=(90, 86, 78), width=3)
d.text(((clx0 + clx1) / 2, (cly0 + cly1) / 2), "06:07", font=f(GOTHIC, 50),
       fill=(238, 176, 84), anchor="mm")
x, i = 240, 0
while x < 1460:
    h = 300 + (i % 3) * 60
    person(d, x + 90, 820, h, (12, 13, 20))
    x += 150
    i += 1
chronicle_tag(d, "ОЧЕРЕДЬ · ПРИЁМНАЯ")
save_base(im, "s6_base.png")

# ================================================================ S7 ПРОХОДНАЯ (КПП) с очередью
# Предложение заказчика 2026-10-11: отдельный кадр — проходная/КПП, куда тянется очередь
# от приёмной; сюда же вешаем плакат «ТЫ НЕ ПРОЙДЁШЬ!».
im = new_base((30, 34, 48), (11, 12, 18))
d = ImageDraw.Draw(im)

# --- асфальт с разметкой
d.rectangle([0, 1120, FW, FH], fill=(16, 18, 26))
for _ in range(16):
    x = random.randint(0, FW); y = random.randint(1130, 1340)
    d.line([(x, y), (x + random.randint(-60, 60), y + random.randint(-12, 12))], fill=(38, 42, 56), width=2)

# --- кирпичный забор (дальний план)
for by in range(520, 1120, 42):
    for bx in range(((by // 42) % 2) * 50, 1560, 100):
        d.rectangle([bx + 2, by + 2, bx + 94, by + 36], fill=(31, 34, 49), outline=(20, 22, 34))
d.rectangle([0, 480, 1560, 520], fill=(44, 46, 60))

# --- БУДКА-ПРОХОДНАЯ (справа)
d.rectangle([1560, 340, FW, 1120], fill=(48, 46, 42))
d.rectangle([1560, 340, FW, 420], fill=(68, 64, 58))
d.rectangle([1640, 520, 1980, 790], fill=(92, 106, 120), outline=(28, 28, 32), width=7)   # окно
d.line([(1810, 520), (1810, 790)], fill=(28, 28, 32), width=5)
d.rectangle([1560, 900, 1640, 1120], fill=(30, 27, 22))                                   # дверь
d.rectangle([1980, 470, 2300, 560], fill=(36, 34, 30))                                    # вывеска
d.text((2140, 486), "ПРОХОДНАЯ", font=f(GOTHIC, 52), fill=GOLD, anchor="ma")

# --- ТУРНИКЕТ у будки
d.rectangle([1470, 780, 1560, 1120], fill=(70, 74, 86))
for yy in range(840, 1100, 64):
    d.line([(1470, yy), (1408, yy - 22)], fill=(112, 118, 132), width=9)
d.ellipse([1470, 748, 1560, 838], fill=(96, 102, 116))

# --- ОЧЕРЕДЬ: змейка людей, тянущаяся от приёмной (слева) к проходной
for row, (yy, dx, col) in enumerate(((820, 0, (12, 13, 20)), (940, 60, (9, 10, 16)))):
    x = 120 + dx
    i = 0
    while x < 1420:
        h = 300 + (i % 3) * 46
        person(d, x + 70, yy, h, col)
        x += 142
        i += 1

# --- ПЛАКАТ «ТЫ НЕ ПРОЙДЁШЬ!» на будке
px0, py0, px1, py1 = 2010, 640, 2290, 830
d.rectangle([px0, py0, px1, py1], fill=(206, 196, 170), outline=(178, 54, 46), width=9)
import math as _m
_cx, _cy, _R = (px0 + px1) / 2, py0 + 34, 22
_star = []
for _k in range(10):
    _r = _R if _k % 2 == 0 else _R * 0.42
    _a = _m.radians(-90 + 36 * _k)
    _star.append((_cx + _r * _m.cos(_a), _cy + _r * _m.sin(_a)))
d.polygon(_star, fill=(196, 54, 44))
d.text((_cx, py0 + 78), "ТЫ НЕ", font=f(GOTHIC, 38), fill=(170, 44, 36), anchor="ma")
d.text((_cx, py0 + 122), "ПРОЙДЁШЬ!", font=f(GOTHIC, 32), fill=(170, 44, 36), anchor="ma")
d.text((_cx, py0 + 162), "ВАХТА · ПРИЁМНАЯ", font=f(LATO_B, 16), fill=(120, 96, 60), anchor="ma")

chronicle_tag(d, "ПРОХОДНАЯ · ОЧЕРЕДЬ")
save_base(im, "s7_base.png")

print("готово: base + оверлеи")
