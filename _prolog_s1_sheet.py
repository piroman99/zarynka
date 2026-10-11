# -*- coding: utf-8 -*-
"""Лист-сравнение S1: советский мок (аниматик) <-> новая проба финала flux-2.
Выход: assets/review/review_57_prolog_s1.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, "assets", "review")
MOCK = os.path.join(HERE, "assets", "mock", "prolog", "s1_base.png")
FLUX = os.path.join(HERE, "assets", "gen", "prolog_s1_cin_0.jpg")

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f = lambda p, s: ImageFont.truetype(p, s)

W = 2020
PW = (W - 3 * 40) // 2           # panel width
PH = int(PW * 9 / 16)
TOP = 150
BOT = 108
canvas = Image.new("RGB", (W, TOP + PH + BOT), (18, 18, 22))
d = ImageDraw.Draw(canvas)

d.text((40, 34), "S1 · подворотня — советская перерисовка", font=f(FB, 54), fill=(240, 240, 245))
d.text((40, 100), "слева — мок аниматика (бесплатно, ~0 ₽)   |   справа — проба финала flux-2 (4.74 ₽)",
       font=f(FR, 26), fill=(160, 160, 172))


def panel(x0, path, label):
    im = Image.open(path).convert("RGB").resize((PW, PH), Image.LANCZOS)
    y0 = TOP + 20
    d.rectangle([x0 - 8, y0 - 8, x0 + PW + 8, y0 + PH + 8], outline=(70, 70, 84), width=3)
    canvas.paste(im, (x0, y0))
    d.text((x0, y0 + PH + 16), label, font=f(FB, 32), fill=(225, 225, 232))


panel(40, MOCK, "АНИМАТИК · мок")
panel(40 + PW + 40, FLUX, "ФИНАЛ · flux-2 (проба)")

d.text((40, TOP + PH + 66),
       "Правка Ивана: «слишком западная подворотня; советская — другая, менее аккуратная» — "
       "облупленный кирпич, арка во двор, труба, лампочка на проводе, контейнеры, лужа, люк, силуэты в кепках.",
       font=f(FR, 24), fill=(150, 150, 162))

out = os.path.join(REV, "review_57_prolog_s1.png")
canvas.save(out)
print("OK", os.path.relpath(out, HERE), canvas.size)
