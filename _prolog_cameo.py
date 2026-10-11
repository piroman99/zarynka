# -*- coding: utf-8 -*-
"""Пасхалка-кандидат: ФИГУРА В ОЧЕРЕДИ (S7 «проходная·очередь»), вид СО СПИНЫ.

Предложение заказчика 2026-10-11: «можем кого-то из героинь Катавы или БЛ поставить в очередь».
Проба-мок (0 ₽): 3 варианта силуэта в очереди + крупный кроп каждого.
Ничего не вкомпоновывается в основной мок — только лист-выборка review_67.

A) ПИОНЕРКА  — белая рубашка + красный галстук + синяя юбка + пилотка (в теме СССР-2061;
   читается как намёк на «Бесконечное лето» — это буквенно советский пионерлагерь).
B) НАМЁК-БЛ — тёмные длинные волосы, синее платье (силуэт, без лица).
C) ШКОЛЬНИЦА-CLASSIC — матросский воротник, тёмная юбка (японский мундир; в советской сцене
   анахронизм + копи-риск) — для сравнения.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, 'assets', 'mock', 'prolog')
REV = os.path.join(HERE, 'assets', 'review')
os.makedirs(REV, exist_ok=True)
GOTH = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

WHITE = (238, 236, 230)
RED = (176, 46, 40)
BLUE = (48, 62, 116)
SKIN = (214, 178, 150)
HAIR_D = (44, 34, 30)
HAIR_BR = (96, 66, 44)


def fig(d, cx, ytop, h, variant):
    """Вид со спины. cx — центр, ytop — макушка, h — рост."""
    r = h * 0.115
    hy = ytop + r
    # ноги
    lw = h * 0.075
    d.rectangle([cx - h * 0.10, ytop + h * 0.62, cx - h * 0.10 + lw, ytop + h], fill=SKIN)
    d.rectangle([cx + h * 0.10 - lw, ytop + h * 0.62, cx + h * 0.10, ytop + h], fill=SKIN)
    if variant in ('A', 'B'):
        d.rectangle([cx - h * 0.115, ytop + h * 0.82, cx - h * 0.02, ytop + h * 0.92], fill=(240, 240, 240))
        d.rectangle([cx + h * 0.02, ytop + h * 0.82, cx + h * 0.115, ytop + h * 0.92], fill=(240, 240, 240))
    # юбка
    if variant == 'A':
        d.polygon([(cx - h * 0.13, ytop + h * 0.52), (cx + h * 0.13, ytop + h * 0.52),
                   (cx + h * 0.20, ytop + h * 0.66), (cx - h * 0.20, ytop + h * 0.66)], fill=BLUE)
    elif variant == 'B':
        d.polygon([(cx - h * 0.12, ytop + h * 0.50), (cx + h * 0.12, ytop + h * 0.50),
                   (cx + h * 0.19, ytop + h * 0.68), (cx - h * 0.19, ytop + h * 0.68)], fill=(40, 48, 86))
    else:
        d.polygon([(cx - h * 0.115, ytop + h * 0.52), (cx + h * 0.115, ytop + h * 0.52),
                   (cx + h * 0.175, ytop + h * 0.68), (cx - h * 0.175, ytop + h * 0.68)], fill=(38, 36, 48))
    # торс / спина
    if variant == 'A':
        d.polygon([(cx - h * 0.115, ytop + h * 0.26), (cx + h * 0.115, ytop + h * 0.26),
                   (cx + h * 0.135, ytop + h * 0.53), (cx - h * 0.135, ytop + h * 0.53)], fill=WHITE)
        # красный галстук = треугольник на спине
        d.polygon([(cx, ytop + h * 0.24), (cx - h * 0.075, ytop + h * 0.30),
                   (cx + h * 0.075, ytop + h * 0.30)], fill=RED)
        d.polygon([(cx - h * 0.02, ytop + h * 0.30), (cx + h * 0.02, ytop + h * 0.30),
                   (cx, ytop + h * 0.46)], fill=RED)
    elif variant == 'B':
        d.polygon([(cx - h * 0.105, ytop + h * 0.26), (cx + h * 0.105, ytop + h * 0.26),
                   (cx + h * 0.125, ytop + h * 0.52), (cx - h * 0.125, ytop + h * 0.52)], fill=(58, 74, 140))
    else:
        d.polygon([(cx - h * 0.11, ytop + h * 0.26), (cx + h * 0.11, ytop + h * 0.26),
                   (cx + h * 0.13, ytop + h * 0.53), (cx - h * 0.13, ytop + h * 0.53)], fill=(150, 150, 165))
        d.polygon([(cx - h * 0.13, ytop + h * 0.245), (cx + h * 0.13, ytop + h * 0.245),
                   (cx + h * 0.145, ytop + h * 0.30), (cx - h * 0.145, ytop + h * 0.30)],
                  fill=(210, 214, 226))  # матросский воротник
    # волосы / голова
    if variant == 'B':
        d.ellipse([cx - h * 0.135, hy - r * 1.15, cx + h * 0.135, ytop + h * 0.44], fill=HAIR_D)
    d.ellipse([cx - r, hy - r, cx + r, hy + r], fill=SKIN)
    if variant == 'A':
        d.ellipse([cx - r * 1.12, hy - r * 1.20, cx + r * 1.12, hy + r * 0.55], fill=HAIR_BR)
        d.ellipse([cx - r * 0.30, hy + r * 0.5, cx - r * 0.02, hy + r * 1.5], fill=HAIR_BR)   # коса
        d.ellipse([cx + r * 0.02, hy + r * 0.5, cx + r * 0.30, hy + r * 1.5], fill=HAIR_BR)   # коса
        # пилотка (красная с белым кантом)
        d.polygon([(cx - r * 1.05, hy - r * 0.55), (cx + r * 1.05, hy - r * 0.55),
                   (cx + r * 0.8, hy - r * 1.35), (cx - r * 0.8, hy - r * 1.35)], fill=RED)
    elif variant == 'B':
        d.ellipse([cx - r * 1.15, hy - r * 1.25, cx + r * 1.15, hy + r * 0.9], fill=HAIR_D)
    else:
        d.ellipse([cx - r * 1.10, hy - r * 1.15, cx + r * 1.10, hy + r * 0.35], fill=(36, 32, 34))


CANDS = [
    ('A', 'A · ПИОНЕРКА (намёк на «Бесконечное лето»)\n      рубашка+галстук+юбка+пилотка — в теме СССР-2061, без копии лица'),
    ('B', 'B · НАМЁК-БЛ — тёмные волосы, синее платье (чистый силуэт, без лица)'),
    ('C', 'C · ШКОЛЬНИЦА-CLASSIC — матросский воротник (японский мундир: анахронизм + копи-риск)'),
]


def build(variant, slot_x=760, row_y=820, h=350):
    im = Image.open(os.path.join(MOCK, 's7_base.png')).convert('RGB')
    d = ImageDraw.Draw(im)
    fig(d, slot_x, row_y, h, variant)
    return im


CW = 1000
PAD, CAPH, HDR = 22, 74, 104
panels = []
for v, cap in CANDS:
    full = build(v)
    crop = full.crop((560, 640, 1060, 1260))
    panels.append((full.resize((CW, round(full.height * CW / full.width)), Image.LANCZOS),
                   crop.resize((CW, round(crop.height * CW / crop.width)), Image.LANCZOS), cap))

H = HDR + sum(f.height + c.height + CAPH + 3 * PAD for f, c, _ in panels) + PAD
sheet = Image.new('RGB', (CW + 2 * PAD, H), (13, 14, 19))
dd = ImageDraw.Draw(sheet)
dd.text((PAD, 18), '«ЗАРЯНКА» · пасхалка-кандидат: ГЕРОИНЯ В ОЧЕРЕДИ (S7)', font=ImageFont.truetype(GOTH, 34), fill=(226, 186, 104))
dd.text((PAD, 62), 'Мок (0 ₽), вид со спины. В основной кадр НЕ вкомпоновано — ждём выбора. '
                   'Персонаж-копия = тот же риск, что и с фанартом конкурса: только силуэт/костюм.',
        font=ImageFont.truetype(LATO_B, 21), fill=(200, 206, 220))

y = HDR
for full, crop, cap in panels:
    sheet.paste(full, (PAD, y)); y += full.height + PAD
    sheet.paste(crop, (PAD, y)); y += crop.height + PAD
    dd.multiline_text((PAD, y), cap, font=ImageFont.truetype(LATO_B, 23), fill=(240, 236, 228), spacing=6)
    y += CAPH + PAD

out = os.path.join(REV, 'review_67_prolog_cameo.png')
sheet.save(out)
print('saved', os.path.relpath(out, HERE), sheet.size)
