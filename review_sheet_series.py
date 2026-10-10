# -*- coding: utf-8 -*-
"""Два контрольных листа: лист персонажа и серия из 5 сцен (nano-banana-2.1)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "review")
os.makedirs(OUT, exist_ok=True)


def font(sz, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()


def fit(im, box):
    im = im.convert("RGB")
    r = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def sheet(items, cols, cell, title, out, topsz=26):
    pad, top = 16, 62
    rows = (len(items) + cols - 1) // cols
    W = pad + cols * (cell[0] + pad)
    H = top + rows * (cell[1] + pad + 30) + pad
    cv = Image.new("RGB", (W, H), (16, 18, 24))
    d = ImageDraw.Draw(cv)
    d.text((pad, 16), title, fill=(240, 240, 245), font=font(topsz, True))
    for i, (lab, rel) in enumerate(items):
        c, r = i % cols, i // cols
        x = pad + c * (cell[0] + pad)
        y = top + r * (cell[1] + pad + 30)
        d.rectangle([x, y, x + cell[0], y + cell[1]], fill=(38, 40, 48))
        p = os.path.join(HERE, rel)
        if os.path.exists(p):
            im = fit(Image.open(p), cell)
            cv.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
        else:
            d.text((x + 12, y + 12), "нет файла", fill=(210, 120, 120), font=font(15))
        d.text((x, y + cell[1] + 7), lab, fill=(212, 216, 224), font=font(15))
    cv.save(out)
    print("saved", out, cv.size)


# --- A. лист персонажа ---
sheet(
    [("Утверждённая Екатерина (референс)", "assets/gen/kate_overalls_0.png"),
     ("Лист персонажа — 4 ракурса (nano-banana-2.1, одна картинка)", "assets/gen/sheet_char_sheet_0.jpg")],
    cols=2, cell=(760, 760),
    title="Зарянка — лист персонажа (Екатерина Ивановна, 68 лет)",
    out=os.path.join(OUT, "review_10_char_sheet.png"),
)

# --- B. серия из 5 сцен ---
labs = ["входит, папка у груди", "протягивает документы",
        "крупный план — говорит", "сидит на краю кресла", "сникла, потухший взгляд"]
items = [("РЕФЕРЕНС: утверждённая Екатерина", "assets/gen/kate_overalls_0.png")]
for (i, l) in enumerate(zip(["c1_enters", "c2_papers", "c3_face", "c4_sits", "c5_sad"], labs)):
    tag = l[0]
    items.append((f"сцена {i+1}: {l[1]}", f"assets/gen/series_{tag}_0.jpg"))
sheet(items, cols=3, cell=(560, 720),
      title="Зарянка — серия из 5 сцен (nano-banana-2.1, референс — тот же, что и лист персонажа)",
      out=os.path.join(OUT, "review_11_series5.png"))
