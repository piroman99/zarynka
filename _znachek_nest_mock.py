# -*- coding: utf-8 -*-
"""Мок: круглое лого B, вписанное в пятиугольник; птица вправо."""
import os, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets', 'review', 'review_30_pentagon_nest.png')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'
BG = (18, 18, 22)
GOLD = (214, 176, 96)
GOLD_D = (150, 116, 52)
GOLD_L = (246, 226, 164)

# круглое лого B (1024x1024, круг: центр 511.5,514 R 391)
SRC = os.path.join(HERE, 'assets', 'gen', 'logo_b_0.jpg')


def font(sz, bold=False):
    return ImageFont.truetype(FONT % ('-Bold' if bold else ''), sz)


def pent(cx, cy, R, rot=-90):
    return [(cx + R * math.cos(math.radians(rot + k * 72)),
             cy + R * math.sin(math.radians(rot + k * 72))) for k in range(5)]


def round_logo(Rc, flip=False):
    """Круглое лого, обрезанное по кругу, радиуса Rc, RGBA."""
    im = Image.open(SRC).convert('RGBA')
    cx0, cy0, R0 = 511.5, 514.0, 391.0
    crop = im.crop((int(cx0 - R0), int(cy0 - R0), int(cx0 + R0), int(cy0 + R0)))
    crop = crop.resize((Rc * 2, Rc * 2), Image.LANCZOS)
    if flip:
        crop = crop.transpose(Image.FLIP_LEFT_RIGHT)
    m = Image.new('L', (Rc * 2, Rc * 2), 0)
    ImageDraw.Draw(m).ellipse([0, 0, Rc * 2 - 1, Rc * 2 - 1], fill=255)
    crop.putalpha(m)
    return crop


def panel(cx, cy, Rc, flipped, label):
    Rp = Rc * 1.30
    # золотая плита-пятиугольник
    dr.polygon(pent(cx, cy, Rp), fill=GOLD_D)
    dr.polygon(pent(cx, cy, Rp - 6), fill=GOLD)
    dr.polygon(pent(cx, cy, Rp - 14), fill=GOLD_L)
    dr.polygon(pent(cx, cy, Rp - 26), fill=GOLD)
    # круглое лого внутри
    lg = round_logo(Rc, flip=flipped)
    sheet.paste(lg, (int(cx - Rc), int(cy - Rc)), lg)
    # золочёный ободок вокруг круга
    dr.ellipse([cx - Rc, cy - Rc, cx + Rc, cy + Rc], outline=GOLD_D, width=4)
    dr.text((cx - 190, cy + Rp + 26), label, font=font(24, True), fill=(230, 230, 235))


W, H = 1720, 1000
sheet = Image.new('RGB', (W, H), BG)
dr = ImageDraw.Draw(sheet)
dr.text((40, 26), 'Значок «Зарянки»: круглое лого вписано в ПЯТИУГОЛЬНИК', font=font(34, True), fill=(255, 130, 120))
dr.text((40, 70), 'птица слева (как сейчас) vs птица справа (предложение заказчика)',
        font=font(19), fill=(165, 165, 175))

panel(330, 470, 250, False, 'ПТИЦА ВЛЕВО (как сейчас)')
panel(880, 470, 250, True, 'ПТИЦА ВПРАВО')
# крупный кадр «птица вправо»
panel(1400, 470, 250, True, '')
dr.text((1400 - 150, 470 + 250 * 1.30 + 26), 'крупно: вправо', font=font(24, True), fill=(230, 230, 235))
# стрелки направления взгляда
dr.text((330 - 24, 470 - 250 * 1.30 - 60), '←', font=font(46, True), fill=(255, 210, 90))
dr.text((880 - 10, 470 - 250 * 1.30 - 60), '→', font=font(46, True), fill=(255, 210, 90))
dr.text((1400 - 10, 470 - 250 * 1.30 - 60), '→', font=font(46, True), fill=(255, 210, 90))

sheet.save(OUT)
print('saved', OUT, sheet.size)
