# -*- coding: utf-8 -*-
"""Превью «что встанет» вместо проблемных мест тизера (ничего не пересобираем).
1) сейчас t=14 (Кейт в платье + размытые полосы)  2) вместо этого: готовый 16:9 с комбинезоном
3) сейчас лого-карточка (белый квадрат)            4) как будет: лого в круге, без квадрата
"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
TMP = os.path.join(HERE, ".tmp_avmcheck")
os.makedirs(TMP, exist_ok=True)
W, H = 1920, 1080

def frame(t, name):
    p = os.path.join(TMP, name)
    subprocess.run([FF, "-y", "-ss", str(t), "-i", os.path.join(HERE, "out", "avm_v3_epic.mp4"),
                    "-frames:v", "1", p], capture_output=True)
    return Image.open(p).convert("RGB")

cur_reception = frame(15, "p_15.png")
cur_card = frame(0.6, "p_0.png")

# --- замена кадра приёмной: готовый 16:9 с комбинезоном
alt = Image.open(os.path.join(HERE, "assets/gen/kate_reception_vn_0.png")).convert("RGB")
alt = alt.resize((W, round(alt.height * W / alt.width)), Image.LANCZOS)
alt = alt.crop((0, max(0, (alt.height - H) // 2), W, max(0, (alt.height - H) // 2) + H)) if alt.height >= H else alt

# --- лого в круге: кремовый диск logo_b обрезаем по кругу, фон -> прозрачный
lg = Image.open(os.path.join(HERE, "assets/gen/logo_b_0.jpg")).convert("RGB")
lg = lg.resize((760, 760), Image.LANCZOS)
mask = Image.new("L", (760, 760), 0)
ImageDraw.Draw(mask).ellipse((10, 10, 749, 749), fill=255)
mask = mask.filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(1.2))
circle = Image.new("RGBA", (760, 760), (0, 0, 0, 0))
circle.paste(lg, (0, 0), mask)

card = Image.new("RGB", (W, H), (11, 13, 18))
card.paste(circle, ((W - 760) // 2, 190), circle)

# --- лист
CW = 900
def fit(im):
    k = CW / im.width
    return im.resize((CW, round(im.height * k)), Image.LANCZOS)

cells = [("СЕЙЧАС  t=15 с — платье + размытые полосы", fit(cur_reception)),
         ("ВМЕСТО  готовый 16:9: Кейт в синем комбинезоне за столом", fit(alt)),
         ("СЕЙЧАС  лого = белый квадрат", fit(cur_card)),
         ("ВМЕСТО  лого в круге (диск с альфой)", fit(card))]
LBL, PAD = 30, 14
rowh = max(c[1].height for c in cells)
sheet = Image.new("RGB", (2 * CW + 3 * PAD, 2 * (rowh + LBL + PAD) + PAD), (16, 18, 24))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 21)
for i, (lab, im) in enumerate(cells):
    r, c = divmod(i, 2)
    x = PAD + c * (CW + PAD)
    y = PAD + r * (rowh + LBL + PAD)
    d.text((x, y), lab, fill=(240, 236, 228), font=f)
    sheet.paste(im, (x, y + LBL))
out = os.path.join(HERE, "assets", "review", "review_106_teaser_fix_preview.png")
sheet.save(out)
print("saved", os.path.relpath(out, HERE), sheet.size)
