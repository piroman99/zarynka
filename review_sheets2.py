# -*- coding: utf-8 -*-
"""Листы: (12) flux-2 vs nano-banana, (13) логотипы. Плюс музыка-каталог печатает отдельно."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "review")


def font(sz, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()


def fit(im, box):
    im = im.convert("RGB")
    r = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def sheet(items, cols, cell, title, out):
    pad, top = 16, 60
    rows = (len(items) + cols - 1) // cols
    W = pad + cols * (cell[0] + pad)
    H = top + rows * (cell[1] + pad + 30) + pad
    cv = Image.new("RGB", (W, H), (16, 18, 24))
    d = ImageDraw.Draw(cv)
    d.text((pad, 16), title, fill=(240, 240, 245), font=font(24, True))
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


# 12 — лист персонажа: nano-banana vs flux-2
sheet(
    [("Утверждённый референс", "refs/kate_master.png"),
     ("nano-banana-2.1", "assets/gen/sheet_char_sheet_0.jpg"),
     ("flux-2", "assets/gen/fxsheet_char_sheet_0.jpg")],
    cols=3, cell=(600, 640),
    title="Лист персонажа: nano-banana-2.1 vs flux-2",
    out=os.path.join(OUT, "review_12_sheet_nb_vs_flux.png"),
)

# 12b — серия 5 сцен: два движка
labs = ["входит", "документы", "крупный план", "сидит", "сникла"]
items = [("РЕФЕРЕНС", "refs/kate_master.png")]
items = [(f"nb-2.1 · {l}", f"assets/gen/series_{t}_0.jpg")
         for l, t in zip(labs, ["c1_enters", "c2_papers", "c3_face", "c4_sits", "c5_sad"])]
items += [(f"flux-2 · {l}", f"assets/gen/fxseries_{t}_0.jpg")
          for l, t in zip(labs, ["c1_enters", "c2_papers", "c3_face", "c4_sits", "c5_sad"])]
sheet(items, cols=5, cell=(400, 520),
      title="Серия 5 сцен: nano-banana-2.1 (верх) vs flux-2 (низ)",
      out=os.path.join(OUT, "review_12b_series_nb_vs_flux.png"))

# 13 — логотипы
sheet(
    [("Оригинал 2016", "assets/orig/icon_large.png"),
     ("вариант A — плоский знак", "assets/gen/logo_a_0.jpg"),
     ("вариант B — медальон", "assets/gen/logo_b_0.jpg"),
     ("вариант C — детальнее", "assets/gen/logo_c_0.jpg")],
    cols=4, cell=(480, 480),
    title="Логотип-зарянка: оригинал и 3 улучшенных варианта",
    out=os.path.join(OUT, "review_13_logo.png"),
)
