# -*- coding: utf-8 -*-
"""Контрольный лист кадров AVM v3 (с реальным движением)."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, ".tmp_diag")

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

labels = [("t=2s", "v3_02.png"), ("t=5s", "v3_05.png"), ("t=9s", "v3_09.png"),
          ("t=13s", "v3_13.png"), ("t=17s", "v3_17.png"), ("t=21s", "v3_21.png"),
          ("t=26s", "v3_26.png"), ("t=30s", "v3_30.png")]
ims = [(l, Image.open(os.path.join(D, f))) for l, f in labels if os.path.exists(os.path.join(D, f))]
CW = 760
CW2 = CW // 2
CW3 = CW // 4
PAD, LBL = 14, 30
cols = 2
W = cols * CW + (cols + 1) * PAD
Hh = ((len(ims) + 1) // 2) * (CW2 + LBL + PAD) + PAD
sheet = Image.new("RGB", (W, Hh), (18, 20, 26))
d = ImageDraw.Draw(sheet)
f = font(22)
for i, (lab, im) in enumerate(ims):
    r, c = divmod(i, cols)
    x = PAD + c * (CW + PAD)
    y = PAD + r * (CW2 + LBL + PAD)
    k = CW / im.width
    im2 = im.resize((CW, round(im.height * k)), Image.LANCZOS)
    d.text((x, y), f"{lab}  (avm_v3)", fill=(235, 232, 226), font=f)
    sheet.paste(im2, (x, y + LBL))
out = os.path.join(HERE, "assets", "review", "review_17_avm_v3.png")
sheet.save(out)
print("saved", os.path.relpath(out, HERE), sheet.size)
