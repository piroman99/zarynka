# -*- coding: utf-8 -*-
"""Лист-выборка по НОВОМУ кадру S7 «ПРОХОДНАЯ · ОЧЕРЕДЬ» (мок, 0 ₽).
Предложение заказчика 2026-10-11: вынести плакат «ТЫ НЕ ПРОЙДЁШЬ!» в отдельную
сцену — проходная/КПП, к которой тянется очередь от приёмной.
Сравниваем: S6 (очередь у приёмной, как было) ↔ S7 (новый кадр) + крупный кроп плаката.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, "assets", "mock", "prolog")
REV = os.path.join(HERE, "assets", "review")
os.makedirs(REV, exist_ok=True)
GOTH = "/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf"
LATO_B = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"

CW = 1000          # ширина картинки в листе
PAD = 22
CAPH = 52
HDR = 104

def load(name, w=CW):
    im = Image.open(os.path.join(MOCK, name)).convert("RGB")
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)

s6 = load("s6_base.png")
s7 = load("s7_base.png")

# крупный кроп плаката из S7 (координаты исходника 2400x1350)
src7 = Image.open(os.path.join(MOCK, "s7_base.png")).convert("RGB")
crop = src7.crop((1540, 400, 2340, 1130))
crop = crop.resize((CW, round(crop.height * CW / crop.width)), Image.LANCZOS)

items = [(s6, "S6 · ОЧЕРЕДЬ у ПРИЁМНОЙ — как было (плакат был тут отдельным мок-слоем)"),
         (s7, "S7 · ПРОХОДНАЯ · ОЧЕРЕДЬ — НОВЫЙ кадр: будка с турникетом, очередь тянется от приёмной,\n"
              "      на будке повешен плакат «ТЫ НЕ ПРОЙДЁШЬ!» (вахта · приёмная)"),
         (crop, "S7 · крупно — будка + турникет + плакат «ТЫ НЕ ПРОЙДЁШЬ!»")]

# считаем высоту
H = HDR + sum(im.height + CAPH + PAD for im, _ in items) + PAD
canvas = Image.new("RGB", (CW + 2 * PAD, H), (13, 14, 19))
d = ImageDraw.Draw(canvas)
d.text((PAD, 18), "«ЗАРЯНКА» · пролог — новый кадр S7 «ПРОХОДНАЯ · ОЧЕРЕДЬ»", font=ImageFont.truetype(GOTH, 34), fill=(226, 186, 104))
d.text((PAD, 62), "Мок (0 ₽). Кадр 2400×1350 → в аниматике 1920×1080, 25 fps. Ждём «го» — вставлять ли S7 в ролик.",
       font=ImageFont.truetype(LATO_B, 22), fill=(200, 206, 220))

y = HDR
for im, cap in items:
    canvas.paste(im, (PAD, y))
    d.rectangle([PAD, y, PAD + im.width, y + im.height], outline=(60, 62, 74))
    d.multiline_text((PAD, y + im.height + 8), cap, font=ImageFont.truetype(LATO_B, 24),
                     fill=(240, 236, 228), spacing=6)
    y += im.height + CAPH + PAD

out = os.path.join(REV, "review_65_prolog_s7_prohodnaya.png")
canvas.save(out)
print("saved", os.path.relpath(out, HERE), canvas.size)
