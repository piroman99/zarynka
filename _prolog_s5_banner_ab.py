# -*- coding: utf-8 -*-
"""S5: варианты текстового слоя (лозунг) поверх ОДНОЙ И ТОЙ ЖЕ плашки. 0 ₽ — генерации нет.

A  — как сейчас: широкая полоса (300..2100 x 500..780) ложится на фасад здания
B  — лента внизу, на пустой площади, одной строкой, не заезжает на автобус
B2 — лента на площади, две строки (ниже A, компактнее)

Плашка: assets/gen/prologfin6_s5_a_0.jpg (кэш, НЕ перегенерируется).
Результат: assets/review/_s5_var{A|B|B2}.png + лист review_97_s5_banner_ab.png
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
REV = os.path.join(HERE, 'assets', 'review')
os.makedirs(REV, exist_ok=True)

FW, FH = 2400, 1350
OUTW, OUTH = 1920, 1080
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
CREAM = (246, 238, 222)


def F(p, s):
    return ImageFont.truetype(p, s)


def load_plate():
    im = Image.open(os.path.join(GEN, 'prologfin6_s5_a_0.jpg')).convert('RGB')
    return im.resize((FW, FH), Image.LANCZOS)


def soft(base, box, color, alpha, blur=16):
    w, h = base.size
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle(box, fill=color + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB')


def tag(base, txt):
    ImageDraw.Draw(base).text((70, 60), txt, font=F(LATO_B, 30), fill=(240, 226, 198))
    return base


def vignette(im, strength=0.75):
    w, h = im.size
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).ellipse([-w * 0.22, -h * 0.30, w * 1.22, h * 1.30], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w // 10))
    dark = Image.new('RGB', (w, h), (0, 0, 0))
    return Image.composite(im, dark, Image.eval(mask, lambda v: 255 - int((255 - v) * strength)))


CONF = {
    # name: (band, chip, chip_alpha, lines)
    'A':  ((300, 500, 2100, 780),   (820, 830, 1580, 920),  232, 'two'),
    'B':  ((240, 1046, 1560, 1176), (600, 1186, 1320, 1256), 210, 'one'),
    'B2': ((240, 1000, 1560, 1196), (600, 1206, 1320, 1276), 214, 'two'),
}


def variant(name):
    band, chip, alpha, mode = CONF[name]
    b = load_plate()
    b = soft(b, band, (168, 40, 34), alpha, blur=10)
    d = ImageDraw.Draw(b)
    x0, y0, x1, y1 = band
    cx = (x0 + x1) / 2
    if mode == 'one':
        d.text((cx, y0 + 64), 'МАРС — ДЕЛО ОБЩЕЕ!  ДАЁШЬ МАРС ДЛЯ ВСЕХ!',
               font=F(GOTHIC, 62), fill=CREAM, anchor='ma')
    else:
        d.text((cx, y0 + 50), 'МАРС — ДЕЛО ОБЩЕЕ!', font=F(GOTHIC, 76), fill=CREAM, anchor='ma')
        d.text((cx, y0 + 142), 'ДАЁШЬ МАРС ДЛЯ ВСЕХ!', font=F(GOTHIC, 62), fill=(252, 226, 170), anchor='ma')
    b = soft(b, chip, (6, 8, 14), 150, blur=14)
    ImageDraw.Draw(b).text(((chip[0] + chip[2]) / 2, (chip[1] + chip[3]) / 2),
                           '2 МЕСТА «С УЛИЦЫ»', font=F(GOTHIC, 46), fill=(255, 210, 120), anchor='mm')
    b = tag(b, 'ЛОЗУНГ · СТРАНА')
    out = vignette(b).resize((OUTW, OUTH), Image.LANCZOS)
    p = os.path.join(REV, '_s5_var%s.png' % name)
    out.save(p)
    print('variant', name, '->', os.path.relpath(p, HERE))
    return out


LABEL = {'A': 'как сейчас — полоса на фасад', 'B': 'лента на площади, одной строкой',
         'B2': 'лента на площади, две строки'}
imgs = {n: variant(n) for n in CONF}

SW = 1100
tiles = []
for n in CONF:
    im = imgs[n].resize((SW, int(SW * OUTH / OUTW)), Image.LANCZOS)
    lab = Image.new('RGB', (SW, 42), (18, 18, 20))
    ImageDraw.Draw(lab).text((14, 8), 'ВАРИАНТ %s — %s' % (n, LABEL[n]),
                             font=F(LATO_B, 24), fill=(238, 226, 200))
    t = Image.new('RGB', (SW, im.size[1] + 42), (18, 18, 20))
    t.paste(lab, (0, 0))
    t.paste(im, (0, 42))
    tiles.append(t)

TH = sum(t.size[1] for t in tiles) + 20 * (len(tiles) - 1)
sheet = Image.new('RGB', (SW, TH), (10, 10, 12))
y = 0
for t in tiles:
    sheet.paste(t, (0, y))
    y += t.size[1] + 20
p = os.path.join(REV, 'review_97_s5_banner_ab.png')
sheet.save(p)
print('sheet ->', os.path.relpath(p, HERE), os.path.getsize(p), 'B')
