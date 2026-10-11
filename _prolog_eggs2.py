# -*- coding: utf-8 -*-
"""Пасхалки пролога — ВЕРСИЯ 2 (правки заказчика 2026-10-11):
  • S1 котобус — оставлен («норм»);
  • S2 — современный транспорт 2061 (не ЛиАЗ), НО номер маршрута 410;
  • S6 часы — 06:07 (валидное время, а не невозможные 6:67);
  • S6_2 — «Ты не пройдёшь!» оформлено ПЛАКАТОМ (оценить, стоит ли);
  • P0 зеркало-птица — помечено «сложно / показать пробой до генерации».
Выход: assets/review/review_60_prolog_eggs.png. Базовые кадры НЕ перезаписываются.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, 'assets', 'mock', 'prolog')
OUT = os.path.join(HERE, 'assets', 'review', 'review_60_prolog_eggs.png')
GOTH = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

FW, FH = 2400, 1350
CHALK = (226, 220, 200, 205)
RED_C = (222, 74, 60)


def ov():
    return Image.new('RGBA', (FW, FH), (0, 0, 0, 0))


def T(p, s):
    return ImageFont.truetype(p, s)


# ---------------- S1 котобус (детский рисунок мелом) — без изменений ----------------
def draw_katobus():
    im = Image.open(os.path.join(MOCK, 's1_base.png')).convert('RGB')
    l = ov(); d = ImageDraw.Draw(l)
    x0, y0, x1, y1 = 165, 815, 470, 955
    d.rounded_rectangle([x0, y0, x1, y1], radius=42, outline=CHALK, width=6)
    d.polygon([(x0 + 60, y0 + 6), (x0 + 108, y0 - 54), (x0 + 150, y0 + 6)], outline=CHALK, width=6)
    d.polygon([(x1 - 150, y0 + 6), (x1 - 108, y0 - 54), (x1 - 60, y0 + 6)], outline=CHALK, width=6)
    for wx in range(x0 + 46, x1 - 40, 74):
        d.rectangle([wx, y0 + 34, wx + 46, y0 + 86], outline=CHALK, width=5)
    for lx in range(x0 + 34, x1 - 30, 62):
        d.line([(lx, y1), (lx, y1 + 58)], fill=CHALK, width=6)
    d.line([(x1 - 4, y0 + 96), (x1 + 66, y0 + 70), (x1 + 74, y0 + 128)], fill=CHALK, width=6)
    d.ellipse([x1 - 96, y0 + 40, x1 - 78, y0 + 58], outline=CHALK, width=5)
    for k in range(3):
        d.line([(x1 - 96, y0 + 74 + k * 12), (x1 - 10, y0 + 62 + k * 16)], fill=CHALK, width=3)
    im = Image.alpha_composite(im.convert('RGBA'), l).convert('RGB')
    return im, (108, 745, 545, 1045), \
        'S1 · КОТОБУС ✅ — детский рисунок мелом на стене (псевдоним автора → Catbus)'


# ---------------- S2 СОВРЕМЕННЫЙ транспорт 2061 с номером 410 ----------------
def draw_modern410():
    im = Image.open(os.path.join(MOCK, 's2_base.png')).convert('RGB')
    l = ov(); d = ImageDraw.Draw(l)
    x0, y0, x1, y1 = 120, 986, 486, 1098
    # корпус — гладкий обтекаемый
    d.rounded_rectangle([x0, y0, x1, y1], radius=34, fill=(172, 180, 196, 255),
                        outline=(96, 104, 122, 255), width=3)
    d.rounded_rectangle([x0 + 6, y0 + 6, x1 - 6, y0 + 40], radius=24, fill=(198, 205, 220, 255))
    # панорамное остекление (тёмная полоса)
    d.rounded_rectangle([x0 + 34, y0 + 40, x1 - 30, y0 + 78], radius=14, fill=(22, 30, 42, 255))
    d.rounded_rectangle([x0 + 40, y0 + 45, x1 - 36, y0 + 55], radius=8, fill=(60, 78, 100, 255))
    # светящаяся маршрутная панель «410»
    d.rounded_rectangle([x0 + 12, y0 + 12, x0 + 96, y0 + 44], radius=8, fill=(12, 14, 20, 255))
    d.text((x0 + 20, y0 + 14), '410', font=T(GOTH, 26), fill=(120, 234, 210, 255))
    # передний блок-фара
    d.rounded_rectangle([x1 - 40, y0 + 18, x1 - 10, y0 + 40], radius=6, fill=(246, 232, 180, 255))
    # акцентная линия и «юбка»
    d.line([(x0 + 20, y1 - 26), (x1 - 20, y1 - 26)], fill=(120, 234, 210, 200), width=3)
    d.rounded_rectangle([x0 + 10, y1 - 14, x1 - 10, y1], radius=6, fill=(60, 66, 80, 255))
    # колёса-обтекатели
    for cx in (x0 + 78, x1 - 78):
        d.ellipse([cx - 30, y1 - 26, cx + 30, y1 + 18], fill=(30, 32, 40, 255))
        d.ellipse([cx - 16, y1 - 12, cx + 16, y1 + 4], fill=(120, 126, 140, 255))
    # блик
    d.line([(x0 + 30, y0 + 20), (x0 + 150, y0 + 12)], fill=(255, 255, 255, 60), width=6)
    im = Image.alpha_composite(im.convert('RGBA'), l).convert('RGB')
    return im, (96, 962, 512, 1122), \
        'S2 · ТРАНСПОРТ-2061 с номером 410 ✅ — современный, но маршрут «410» на месте'


# ---------------- S6 цифровые часы 06:07 ----------------
def draw_clock():
    im = Image.open(os.path.join(MOCK, 's6_base.png')).convert('RGB')
    l = ov(); d = ImageDraw.Draw(l)
    x0, y0, x1, y1 = 1552, 536, 1772, 614
    d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=(16, 18, 20, 255), outline=(90, 86, 78, 255), width=3)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), '06:07', font=T(GOTH, 50),
           fill=(238, 176, 84, 255), anchor='mm')
    im = Image.alpha_composite(im.convert('RGBA'), l).convert('RGB')
    return im, (1512, 498, 1812, 652), \
        'S6 · ЧАСЫ 06:07 ✅ — валидное время, но читается «шесть-семь» (мем six-seven)'


# ---------------- S6_2 «Ты не пройдёшь!» ПЛАКАТОМ ----------------
def draw_poster():
    im = Image.open(os.path.join(MOCK, 's6_base.png')).convert('RGB')
    l = ov(); d = ImageDraw.Draw(l)
    x0, y0, x1, y1 = 1852, 540, 2178, 706
    d.rectangle([x0, y0, x1, y1], fill=(206, 196, 170, 255))
    d.rectangle([x0, y0, x1, y1], outline=(178, 54, 46, 255), width=10)        # красная рамка
    # пятиконечная звезда сверху
    import math
    cx, cy, R = (x0 + x1) / 2, y0 + 34, 22
    pts = []
    for k in range(10):
        r = R if k % 2 == 0 else R * 0.42
        a = math.radians(-90 + 36 * k)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=(196, 54, 44, 255))
    d.text((cx, y0 + 78), 'ТЫ НЕ', font=T(GOTH, 34), fill=(170, 44, 36, 255), anchor='ma')
    d.text((cx, y0 + 116), 'ПРОЙДЁШЬ!', font=T(GOTH, 30), fill=(170, 44, 36, 255), anchor='ma')
    d.text((cx, y0 + 150), 'ВАХТА · ПРИЁМНАЯ', font=T(LATO_B, 15), fill=(120, 96, 60, 255), anchor='ma')
    # гвоздики по углам
    for gx, gy in ((x0 + 12, y0 + 12), (x1 - 12, y0 + 12), (x0 + 12, y1 - 12), (x1 - 12, y1 - 12)):
        d.ellipse([gx - 4, gy - 4, gx + 4, gy + 4], fill=(90, 84, 72, 255))
    im = Image.alpha_composite(im.convert('RGBA'), l).convert('RGB')
    return im, (1826, 516, 2204, 730), \
        'S6_2 · «ТЫ НЕ ПРОЙДЁШЬ!» — плакатом на стене (оценить: нужен ли)'


# ---------------- P0 зеркало-птица (помечено «сложно») ----------------
def draw_mirror():
    frame = Image.new('RGB', (FW, FH), (8, 10, 20))
    glow = Image.new('L', (FW, FH), 0)
    ImageDraw.Draw(glow).ellipse([760, 120, 1640, 1240], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    frame = Image.composite(Image.new('RGB', (FW, FH), (26, 28, 46)), frame, glow)

    _src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
    _ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
    exec(compile(_src, '_znak3d.py', 'exec'), _ns)
    zn = _ns['render'](180, w=900, h=900)
    frame.paste(zn, (750, 225))

    l = ov(); d = ImageDraw.Draw(l)
    d.ellipse([1055, 470, 1405, 720], fill=(255, 255, 255, 22))
    bx, by, s = 1210, 612, 34
    d.ellipse([bx - s, by - .74 * s, bx + s, by + .74 * s], fill=(58, 52, 56, 255))
    d.ellipse([bx + .2 * s, by - 1.2 * s, bx + 1.2 * s, by - .2 * s], fill=(58, 52, 56, 255))
    d.ellipse([bx + .15 * s, by - .25 * s, bx + 1.05 * s, by + .85 * s], fill=(214, 122, 66, 255))
    d.polygon([(bx - s, by - .2 * s), (bx - 2.2 * s, by - .6 * s), (bx - 2.0 * s, by + .1 * s),
               (bx - s, by + .3 * s)], fill=(46, 42, 46, 255))
    d.polygon([(bx + 1.2 * s, by - .8 * s), (bx + 1.8 * s, by - .7 * s), (bx + 1.2 * s, by - .55 * s)],
              fill=(220, 190, 90, 255))
    d.line([(bx - .1 * s, by + .7 * s), (bx - .1 * s, by + 1.05 * s)], fill=(40, 38, 40, 255), width=3)
    d.line([(bx + .4 * s, by + .7 * s), (bx + .4 * s, by + 1.05 * s)], fill=(40, 38, 40, 255), width=3)
    # штамп «на паузе»
    d.rounded_rectangle([700, 60, 1700, 170], radius=10, fill=(0, 0, 0, 150))
    d.text((1200, 86), 'СЛОЖНО · НА ПАУЗЕ', font=T(GOTH, 44), fill=(255, 150, 120, 255), anchor='ma')
    d.text((1200, 140), 'показать пробой flux-2 (~3.4 ₽) ДО генерации финала',
           font=T(LATO_B, 24), fill=(230, 226, 220, 255), anchor='ma')
    frame = Image.alpha_composite(frame.convert('RGBA'), l).convert('RGB')
    return frame, (1040, 440, 1420, 790), \
        'P0 · ПТИЦА В ОТРАЖЕНИИ — сложно; сначала показать пробой, потом решать'


ROWS = [draw_katobus(), draw_modern410(), draw_clock(), draw_poster(), draw_mirror()]

LW = RW = 780
PH = round(LW * FH / FW)
pad, gap, hdr, caph = 24, 14, 138, 66
W = pad * 2 + LW + gap + RW
H = hdr + len(ROWS) * (PH + caph + 16) + pad
canvas = Image.new('RGB', (W, H), (13, 14, 19))
d = ImageDraw.Draw(canvas)
d.text((pad, 16), '«ЗАРЯНКА» · пролог — пасхалки, v2 (по правкам)',
       font=T(GOTH, 32), fill=(226, 186, 104))
d.text((pad, 58), 'S1 оставлен · S2 современный с №410 · часы 06:07 · «Ты не пройдёшь!» плакатом · зеркало — на паузе.',
       font=T(LATO_B, 21), fill=(206, 211, 230))
d.text((pad, 84), 'Слева — кадр с обводкой, справа — зум. Скажи, что берём — вкомпоную в моки (0 ₽).',
       font=T(LATO_B, 21), fill=(206, 211, 230))
d.text((pad, 110), 'Уже есть и ждёт «смотреть»: гравировка ребра значка «ЛМД» (лист review_61, черновик вращения znak3d_rot_draft.mp4).',
       font=T(LATO_B, 21), fill=(150, 205, 150))

y = hdr
for frame, (x0, y0, x1, y1), cap in ROWS:
    mark = frame.copy()
    ImageDraw.Draw(mark).ellipse([x0 - 8, y0 - 8, x1 + 8, y1 + 8], outline=RED_C, width=7)
    mark = mark.resize((LW, PH), Image.LANCZOS)
    canvas.paste(mark, (pad, y))
    cw, ch = x1 - x0, y1 - y0
    crop = frame.crop((x0, y0, x1, y1))
    sc = min(RW / cw, PH / ch)
    crop = crop.resize((max(1, int(cw * sc)), max(1, int(ch * sc))), Image.LANCZOS)
    panel = Image.new('RGB', (RW, PH), (8, 9, 13))
    panel.paste(crop, ((RW - crop.width) // 2, (PH - crop.height) // 2))
    pd = ImageDraw.Draw(panel)
    pd.rectangle([0, 0, RW - 1, PH - 1], outline=(80, 82, 96))
    pd.text((8, PH - 30), 'зум', font=T(LATO_B, 20), fill=(200, 204, 216))
    canvas.paste(panel, (pad + LW + gap, y))
    d.text((pad, y + PH + 8), cap, font=T(LATO_B, 23), fill=(240, 236, 228))
    y += PH + caph + 16

canvas.save(OUT)
print('saved', os.path.relpath(OUT, HERE), canvas.size)
