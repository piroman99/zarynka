# -*- coding: utf-8 -*-
"""Лист пасхалок пролога: 5 «двойных дна» по кадрам (мок, 0 ₽).
Левый панель — кадр целиком (пасхалка обведена), правая — зум-кроп.
Плюс напоминание про уже существующую гравировку на ребре значка.
Выход: assets/review/review_59_prolog_eggs.png. Базовые кадры НЕ перезаписываются.
"""
import os, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, 'assets', 'mock', 'prolog')
OUT = os.path.join(HERE, 'assets', 'review', 'review_59_prolog_eggs.png')
GOTH = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

FW, FH = 2400, 1350
CHALK = (226, 220, 200, 205)
RED_C = (222, 74, 60)

# 3D-значок (для P0)
sys.path.insert(0, HERE)
_src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
_ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(_src, '_znak3d.py', 'exec'), _ns)
render3d = _ns['render']


def ov():
    return Image.new('RGBA', (FW, FH), (0, 0, 0, 0))


# ---------------- S1 котобус (детский рисунок мелом) ----------------
def draw_katobus():
    im = Image.open(os.path.join(MOCK, 's1_base.png')).convert('RGB')
    l = ov(); d = ImageDraw.Draw(l)
    x0, y0, x1, y1 = 165, 815, 470, 955          # тело
    d.rounded_rectangle([x0, y0, x1, y1], radius=42, outline=CHALK, width=6)
    d.polygon([(x0 + 60, y0 + 6), (x0 + 108, y0 - 54), (x0 + 150, y0 + 6)], outline=CHALK, width=6)  # ухо 1
    d.polygon([(x1 - 150, y0 + 6), (x1 - 108, y0 - 54), (x1 - 60, y0 + 6)], outline=CHALK, width=6)  # ухо 2
    for wx in range(x0 + 46, x1 - 40, 74):       # «окна»-вагон
        d.rectangle([wx, y0 + 34, wx + 46, y0 + 86], outline=CHALK, width=5)
    for lx in range(x0 + 34, x1 - 30, 62):       # лапы
        d.line([(lx, y1), (lx, y1 + 58)], fill=CHALK, width=6)
    d.line([(x1 - 4, y0 + 96), (x1 + 66, y0 + 70), (x1 + 74, y0 + 128)], fill=CHALK, width=6)  # хвост
    d.ellipse([x1 - 96, y0 + 40, x1 - 78, y0 + 58], outline=CHALK, width=5)   # глаз
    for k in range(3):                            # усы
        d.line([(x1 - 96, y0 + 74 + k * 12), (x1 - 10, y0 + 62 + k * 16)], fill=CHALK, width=3)
    im = Image.alpha_composite(im.convert('RGBA'), l).convert('RGB')
    return im, (108, 745, 545, 1045), \
        'S1 · КОТОБУС — детский рисунок мелом на стене (автор «Котобус» → Catbus)'


# ---------------- S2 автобус 410 / ЛиАЗ-677 ----------------
def draw_bus410():
    im = Image.open(os.path.join(MOCK, 's2_base.png')).convert('RGB')
    l = ov(); d = ImageDraw.Draw(l)
    x0, y0, x1, y1 = 140, 1002, 452, 1094
    d.rounded_rectangle([x0, y0, x1, y1], radius=20, fill=(150, 146, 120, 255), outline=(70, 68, 54, 255), width=3)
    for wx in range(x0 + 22, x1 - 34, 62):        # окна (тёплый свет)
        d.rectangle([wx, y0 + 22, wx + 46, y0 + 60], fill=(226, 196, 130, 255))
    d.rectangle([x0 + 10, y1 - 20, x1 - 10, y1 - 4], fill=(60, 58, 46, 255))   # подножка/юбка
    for cx in (x0 + 60, x1 - 60):                 # колёса
        d.ellipse([cx - 24, y1 - 22, cx + 24, y1 + 20], fill=(24, 24, 26, 255))
    d.rectangle([x0 + 14, y0 + 4, x0 + 74, y0 + 30], fill=(30, 30, 32, 255))    # маршрутная табличка
    d.text((x0 + 44, y0 + 6), '410', font=ImageFont.truetype(LATO_B, 20), fill=(240, 214, 150, 255), anchor='ma')
    d.text(((x0 + x1) / 2, y1 - 26), 'ЛиАЗ-677', font=ImageFont.truetype(LATO_B, 15),
           fill=(236, 230, 210, 210), anchor='ma')
    im = Image.alpha_composite(im.convert('RGBA'), l).convert('RGB')
    return im, (118, 978, 475, 1120), \
        'S2 · АВТОБУС 410 / ЛиАЗ-677 — старый автобус на краю космодрома (отсылка: «Бесконечное лето»)'


# ---------------- S6 цифровые часы 6:67 ----------------
def draw_clock():
    im = Image.open(os.path.join(MOCK, 's6_base.png')).convert('RGB')
    l = ov(); d = ImageDraw.Draw(l)
    x0, y0, x1, y1 = 1560, 536, 1770, 616
    d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=(16, 18, 20, 255), outline=(90, 86, 78, 255), width=3)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), '6:67', font=ImageFont.truetype(GOTH, 52),
           fill=(238, 176, 84, 255), anchor='mm')
    im = Image.alpha_composite(im.convert('RGBA'), l).convert('RGB')
    return im, (1520, 500, 1810, 650), \
        'S6 · ЧАСЫ 6:67 — невозможное время (мем six-seven)'


# ---------------- S6 табличка «Ты не пройдёшь!» ----------------
def draw_plaque():
    im = Image.open(os.path.join(MOCK, 's6_base.png')).convert('RGB')
    l = ov(); d = ImageDraw.Draw(l)
    x0, y0, x1, y1 = 1556, 664, 1774, 756
    d.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=(120, 96, 44, 255), outline=(196, 164, 92, 255), width=3)
    d.text(((x0 + x1) / 2, y0 + 22), 'ТЫ НЕ', font=ImageFont.truetype(GOTH, 30), fill=(250, 240, 214, 255), anchor='ma')
    d.text(((x0 + x1) / 2, y0 + 58), 'ПРОЙДЁШЬ!', font=ImageFont.truetype(GOTH, 30), fill=(250, 240, 214, 255), anchor='ma')
    im = Image.alpha_composite(im.convert('RGBA'), l).convert('RGB')
    return im, (1516, 628, 1814, 790), \
        'S6 · «ТЫ НЕ ПРОЙДЁШЬ!» — табличка у вахты (Толкин: вахтёрша не пускает… потом пускает)'


# ---------------- P0 птица в отражении (зеркало) ----------------
def draw_mirror():
    frame = Image.new('RGB', (FW, FH), (8, 10, 20))
    # лёгкая радиальная подсветка
    glow = Image.new('L', (FW, FH), 0)
    ImageDraw.Draw(glow).ellipse([760, 120, 1640, 1240], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    frame = Image.composite(Image.new('RGB', (FW, FH), (26, 28, 46)), frame, glow)
    zn = render3d(180, w=900, h=900)
    # прозрачность = тёмный фон значка почти совпадает с кадром
    frame.paste(zn, (750, 225))
    l = ov(); d = ImageDraw.Draw(l)
    # блик на стекле иллюминатора
    d.ellipse([1055, 470, 1405, 720], fill=(255, 255, 255, 26))
    # птица-зарянка (отражение)
    bx, by, s = 1210, 612, 34
    d.ellipse([bx - s, by - .74 * s, bx + s, by + .74 * s], fill=(58, 52, 56, 255))          # спина/тело
    d.ellipse([bx + .2 * s, by - 1.2 * s, bx + 1.2 * s, by - .2 * s], fill=(58, 52, 56, 255))  # голова
    d.ellipse([bx + .15 * s, by - .25 * s, bx + 1.05 * s, by + .85 * s], fill=(214, 122, 66, 255))  # грудка
    d.polygon([(bx - s, by - .2 * s), (bx - 2.2 * s, by - .6 * s), (bx - 2.0 * s, by + .1 * s),
               (bx - s, by + .3 * s)], fill=(46, 42, 46, 255))                                # хвост
    d.polygon([(bx + 1.2 * s, by - .8 * s), (bx + 1.8 * s, by - .7 * s), (bx + 1.2 * s, by - .55 * s)],
              fill=(220, 190, 90, 255))                                                       # клюв
    d.line([(bx - .1 * s, by + .7 * s), (bx - .1 * s, by + 1.05 * s)], fill=(40, 38, 40, 255), width=3)
    d.line([(bx + .4 * s, by + .7 * s), (bx + .4 * s, by + 1.05 * s)], fill=(40, 38, 40, 255), width=3)
    frame = Image.alpha_composite(frame.convert('RGBA'), l).convert('RGB')
    return frame, (1040, 440, 1420, 790), \
        'P0 · ПТИЦА В ОТРАЖЕНИИ — в стекле иллюминатора мелькает зарянка (пасхалка-ЗЕРКАЛО)'


ROWS = [draw_katobus(), draw_bus410(), draw_clock(), draw_plaque(), draw_mirror()]

# ---------------- сборка листа ----------------
LW = 780
PH = round(LW * FH / FW)                      # 439
RW = 780
pad, gap, hdr, caph = 24, 14, 118, 66
W = pad * 2 + LW + gap + RW
row_h = PH + caph + 16
H = hdr + len(ROWS) * row_h + pad
canvas = Image.new('RGB', (W, H), (13, 14, 19))
d = ImageDraw.Draw(canvas)
d.text((pad, 16), '«ЗАРЯНКА» · пролог — пасхалки по кадрам (меню из 5)',
       font=ImageFont.truetype(GOTH, 32), fill=(226, 186, 104))
d.text((pad, 58), 'Двойное дно: незнающий видит деталь, знающий улыбается. Всё локально (0 ₽), шить в мок — по согласованию.',
       font=ImageFont.truetype(LATO_B, 21), fill=(206, 211, 230))
d.text((pad, 84), 'Уже есть: гравировка на ребре значка ЛМД · Ц. 67 КОП. (пасхалка на P0).',
       font=ImageFont.truetype(LATO_B, 21), fill=(150, 205, 150))

y = hdr
for frame, (x0, y0, x1, y1), cap in ROWS:
    # левая панель: кадр + обводка
    mark = frame.copy()
    ImageDraw.Draw(mark).ellipse([x0 - 8, y0 - 8, x1 + 8, y1 + 8], outline=RED_C, width=7)
    mark = mark.resize((LW, PH), Image.LANCZOS)
    canvas.paste(mark, (pad, y))
    # правая панель: зум-кроп (contain)
    cw, ch = x1 - x0, y1 - y0
    crop = frame.crop((x0, y0, x1, y1))
    sc = min(RW / cw, PH / ch)
    crop = crop.resize((max(1, int(cw * sc)), max(1, int(ch * sc))), Image.LANCZOS)
    panel = Image.new('RGB', (RW, PH), (8, 9, 13))
    panel.paste(crop, ((RW - crop.width) // 2, (PH - crop.height) // 2))
    pd = ImageDraw.Draw(panel)
    pd.rectangle([0, 0, RW - 1, PH - 1], outline=(80, 82, 96))
    pd.text((8, PH - 30), 'зум', font=ImageFont.truetype(LATO_B, 20), fill=(200, 204, 216))
    canvas.paste(panel, (pad + LW + gap, y))
    # подпись
    d.text((pad, y + PH + 8), cap, font=ImageFont.truetype(LATO_B, 23), fill=(240, 236, 228))
    y += row_h

canvas.save(OUT)
print('saved', os.path.relpath(OUT, HERE), canvas.size)
