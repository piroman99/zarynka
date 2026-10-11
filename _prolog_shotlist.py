# -*- coding: utf-8 -*-
"""Раскадровка пролога-клипа «Зарянка» + таймлайн (полоса времени).
Схематические кадры (PIL) + тайм-шифт. 0 ₽, без генерации.
Выход: assets/review/review_53_prolog_shotlist.png
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.join(HERE, 'assets', 'review')
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

GOLD = (214, 176, 96)
CREAM = (248, 240, 225)
INK = (16, 18, 26)
BLU = (90, 150, 220)
RED = (220, 90, 80)

PW, PH = 480, 270           # панель 16:9
COLS, ROWS = 4, 2
M = 20                      # отступ
HDR = 66
TL_H = 150
FW = COLS * PW + (COLS + 1) * M
FH = HDR + ROWS * PH + (ROWS + 1) * M + TL_H


def f(path, sz):
    return ImageFont.truetype(path, sz)


SHEET = Image.new('RGB', (FW, FH), (12, 12, 16))
D = ImageDraw.Draw(SHEET)
D.text((M, 16), '«ЗАРЯНКА» — пролог-клип · РАСКАДРОВКА + ТАЙМ-ШИФТ (гибрид, ~1:28 до Приёмной)',
       font=f(GOTHIC, 30), fill=(255, 200, 120))
D.text((M, 48), 'схема кадра   ·   интро-значок 3D (К2) → хроника-пролог → передача в интерактивную Приёмную',
       font=f(LATO, 18), fill=(150, 155, 170))


def frame(x, y):
    im = Image.new('RGB', (PW, PH), (18, 20, 30))
    d = ImageDraw.Draw(im)
    return im, d


def tag(d, n, t0, t1, title, sub):
    d.rectangle([0, 0, PW, 56], fill=(8, 9, 14))
    d.text((10, 6), n, font=f(GOTHIC, 22), fill=(255, 210, 120))
    d.text((PW - 10, 6), '%s–%s' % (t0, t1), font=f(LATO_B, 18), fill=(255, 160, 130), anchor='ra')
    d.text((10, 30), title, font=f(GOTHIC, 18), fill=CREAM)
    d.text((PW - 10, 32), sub, font=f(LATO, 15), fill=(150, 200, 240), anchor='ra')


def pent(d, cx, cy, R, fill, out=None, wdt=3, rot=-90):
    pts = [(cx + R * math.cos(math.radians(rot + 72 * k)),
            cy + R * math.sin(math.radians(rot + 72 * k))) for k in range(5)]
    d.polygon(pts, fill=fill, outline=out)
    return pts


# ---------- P0: интро-значок ----------
im, d = frame(0, 0)
d.rectangle([0, 56, PW, PH], fill=(6, 7, 14))
pent(d, PW / 2, 175, 62, (28, 24, 16), GOLD, 3)
# птица-силуэт внутри
d.polygon([(PW / 2 - 26, 176), (PW / 2 + 20, 158), (PW / 2 + 6, 176),
           (PW / 2 + 24, 196), (PW / 2 - 20, 186)], fill=GOLD)
d.rectangle([PW / 2 - 3, 96, PW / 2 + 3, 236], fill=(120, 96, 44))   # РЕБРО (грань)
d.text((PW / 2, 250), 'ребро: пасхалка «ЛМД · Ц. 67 КОП.»', font=f(LATO, 15),
       fill=(230, 180, 120), anchor='ma')
tag(d, 'P0', '0:00', '0:08', 'ИНТРО-ЗНАЧОК (3D К2)', 'муз. стинг')
SHEET.paste(im, (M, HDR + M))

# ---------- P1: подворотня ----------
im, d = frame(0, 0)
d.rectangle([0, 56, PW, PH], fill=(20, 24, 40))
for i, bx in enumerate((30, 120, 300, 400)):
    d.rectangle([bx, 120 - i * 12, bx + 70, PH], fill=(28, 32, 52))
d.ellipse([210, 150, 250, 240], fill=(10, 10, 16))           # силуэт
d.rectangle([222, 176, 238, 240], fill=(10, 10, 16))
d.text((60, 78), 'МАРС — ДЕЛО ОБЩЕЕ?', font=f(GOTHIC, 20), fill=(230, 210, 170))
for i in range(6):
    d.line([(0, 60 + i * 3), (PW, 60 + i * 3)], fill=(40, 44, 60))
tag(d, 'S1', '0:08', '0:20', 'ТЁМНАЯ ПОДВОРОТНЯ', 'хроника, зерно')
SHEET.paste(im, (M + (PW + M), HDR + M))

# ---------- P2: Звёздный городок / сборка ----------
im, d = frame(0, 0)
d.rectangle([0, 56, PW, PH], fill=(24, 34, 54))
d.line([(0, 200), (PW, 200)], fill=(60, 70, 95), width=2)
d.polygon([(150, 200), (185, 90), (220, 200)], fill=(200, 205, 215))  # ракета
d.polygon([(170, 150), (185, 90), (200, 150)], fill=RED)
d.rectangle([250, 150, 340, 200], fill=(150, 160, 180))               # модуль
d.rectangle([360, 130, 450, 200], fill=(120, 130, 150))
for i in range(7):
    d.ellipse([80 + i * 45, 210, 90 + i * 45, 224], fill=(90, 100, 125))  # люди
tag(d, 'S2', '0:20', '0:34', 'ЗВЁЗДНЫЙ ГОРОДОК', 'сборка · тренировки')
SHEET.paste(im, (M + 2 * (PW + M), HDR + M))

# ---------- P3: «Марс — дело общее?» ----------
im, d = frame(0, 0)
d.rectangle([0, 56, PW, PH], fill=(26, 30, 46))
d.rectangle([120, 90, 360, 210], fill=(40, 60, 90), outline=BLU, width=3)
d.text((240, 118), 'МАРС —', font=f(GOTHIC, 26), fill=CREAM, anchor='ma')
d.text((240, 152), 'ДЕЛО ОБЩЕЕ?', font=f(GOTHIC, 26), fill=(255, 210, 120), anchor='ma')
d.text((240, 190), '«Общее!»', font=f(LATO, 18), fill=(150, 210, 150), anchor='ma')
for i in range(9):
    d.ellipse([30 + i * 50, 232, 44 + i * 50, 246], fill=(80, 88, 110))
tag(d, 'S3', '0:34', '0:48', '«А ОБЫЧНЫХ ЛЮДЕЙ НЕТ?»', 'хор голосов')
SHEET.paste(im, (M + 3 * (PW + M), HDR + M))

# ---------- P4: видеоролик ----------
im, d = frame(0, 0)
d.rectangle([0, 56, PW, PH], fill=(14, 16, 26))
d.rectangle([110, 86, 370, 214], fill=(10, 30, 50), outline=(120, 120, 140), width=2)
d.ellipse([300, 150, 356, 206], fill=(180, 120, 90))     # планета
for i in range(10):
    d.point((130 + (i * 37) % 210, 100 + (i * 23) % 90), fill=(200, 210, 230))  # звёзды
d.polygon([(210, 130), (210, 175), (250, 152)], fill=(230, 230, 230))           # play
for i in range(10):
    d.line([(80, 70 + i * 14), (400, 70 + i * 14)], fill=(30, 34, 46))
tag(d, 'S4', '0:48', '1:00', 'СЛЕПЛЕННЫЙ РОЛИК', 'нарезка + вопрос')
SHEET.paste(im, (M, HDR + M + (PH + M)))

# ---------- P5: лозунг облетел страну ----------
im, d = frame(0, 0)
d.rectangle([0, 56, PW, PH], fill=(28, 26, 40))
d.polygon([(90, 100), (250, 78), (330, 150), (240, 220), (110, 210), (60, 150)],
          fill=(40, 60, 80), outline=(90, 110, 140))
for i in range(5):
    d.rectangle([70 + i * 70, 120 + (i % 2) * 30, 130 + i * 70, 180 + (i % 2) * 30],
                fill=(200, 90, 80))
d.text((240, 240), '2 МЕСТА «С УЛИЦЫ»', font=f(GOTHIC, 20), fill=(255, 210, 120), anchor='ma')
tag(d, 'S5', '1:00', '1:14', 'ЛОЗУНГ ОБЛЕТЕЛ СТРАНУ', 'Верховный Совет')
SHEET.paste(im, (M + (PW + M), HDR + M + (PH + M)))

# ---------- P6: очередь ----------
im, d = frame(0, 0)
d.rectangle([0, 56, PW, PH], fill=(30, 30, 40))
d.rectangle([280, 96, 450, PH], fill=(60, 54, 44))          # здание приёмной
d.text((365, 120), 'ПРИЁМНАЯ', font=f(GOTHIC, 18), fill=(255, 210, 120), anchor='ma')
d.rectangle([330, 150, 400, 200], fill=(30, 26, 20))
for i in range(7):
    x = 40 + i * 34
    d.ellipse([x, 176, x + 16, 192], fill=(120, 130, 155))
    d.rectangle([x + 5, 192, x + 11, 230], fill=(100, 110, 135))
tag(d, 'S6', '1:14', '1:28', 'ОЧЕРЕДЬ ЗА МЕЧТОЙ', '→ в Приёмную')
SHEET.paste(im, (M + 2 * (PW + M), HDR + M + (PH + M)))

# ---------- P7: переход в VN ----------
im, d = frame(0, 0)
d.rectangle([0, 56, PW, PH], fill=(34, 30, 26))
d.rectangle([0, 200, PW, PH], fill=(80, 62, 44))
d.rectangle([150, 90, 330, 230], fill=(60, 48, 36), outline=(120, 96, 70), width=2)  # стол
d.ellipse([220, 96, 262, 140], fill=(220, 220, 225))       # седая голова
d.rectangle([226, 140, 256, 210], fill=(60, 90, 170))      # синий комбинезон
d.text((240, 246), '▶ ДАЛЬШЕ — ЖИВОЙ ТЕКСТ АВТОРА', font=f(LATO, 15),
       fill=(255, 210, 120), anchor='ma')
tag(d, 'VN', '1:28', '→', 'ПРИЁМНАЯ (интерактив)', 'клик · текст автора')
SHEET.paste(im, (M + 3 * (PW + M), HDR + M + (PH + M)))

# ---------- ТАЙМЛАЙН ----------
TY = HDR + ROWS * PH + (ROWS + 1) * M
D.rectangle([M, TY, FW - M, TY + TL_H - 10], fill=(16, 16, 22))
D.text((M + 14, TY + 8), 'ТАЙМ-ШИФТ  (0:00 → 1:28 клип, далее интерактив)',
       font=f(GOTHIC, 20), fill=(255, 200, 120))
bx0, bx1 = M + 30, FW - M - 30
by = TY + 84
bh = 26
# деления по 10 c
D.line([(bx0, by + bh + 6), (bx1, by + bh + 6)], fill=(90, 95, 110), width=2)
total = 88.0
for sec in range(0, 91, 10):
    x = bx0 + (bx1 - bx0) * sec / total
    D.line([(x, by + bh + 6), (x, by + bh + 14)], fill=(90, 95, 110), width=2)
    D.text((x, by + bh + 18), '0:%02d' % sec if sec < 60 else '%d:%02d' % (sec // 60, sec % 60),
           font=f(LATO, 14), fill=(150, 155, 170), anchor='ma')
beats = [('P0', 0, 8, (170, 140, 70)), ('S1', 8, 12, (60, 70, 100)),
         ('S2', 20, 14, (60, 90, 130)), ('S3', 34, 14, (70, 80, 130)),
         ('S4', 48, 12, (50, 80, 110)), ('S5', 60, 14, (150, 70, 70)),
         ('S6', 74, 14, (70, 100, 90))]
for nm, a, dd, col in beats:
    x0 = bx0 + (bx1 - bx0) * a / total
    x1 = bx0 + (bx1 - bx0) * (a + dd) / total
    D.rectangle([x0, by, x1, by + bh], fill=col, outline=(20, 20, 26))
    D.text(((x0 + x1) / 2, by + bh / 2), nm, font=f(GOTHIC, 16), fill=CREAM, anchor='mm')
# маркеры-события
ev = [(0, 'значок'), (8, 'проявление S1'), (74, 'очередь'), (88, 'VN')]
for sec, lb in ev:
    x = bx0 + (bx1 - bx0) * sec / total
    D.line([(x, by - 16), (x, by + bh + 6)], fill=(255, 210, 120), width=1)
    D.text((x, by - 32), lb, font=f(LATO, 13), fill=(255, 210, 120), anchor='ma')
# полная версия (~1:50) — метка
xf = bx0 + (bx1 - bx0) * 110 / total
D.text((FW - M - 14, TY + 8), 'полная версия ~1:50 →', font=f(LATO, 16),
       fill=(150, 155, 170), anchor='ra')

os.makedirs(REVIEW, exist_ok=True)
out = os.path.join(REVIEW, 'review_53_prolog_shotlist.png')
SHEET.save(out)
print('saved', os.path.relpath(out, HERE), SHEET.size)
