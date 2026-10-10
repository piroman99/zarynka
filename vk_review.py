# -*- coding: utf-8 -*-
"""Контрольный лист оформления ВК: обложка (2.5:1), аватары и мок с наложенным аватаром."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VK = os.path.join(HERE, "assets", "vk")
REV = os.path.join(HERE, "assets", "review")
os.makedirs(REV, exist_ok=True)
F = "/usr/share/fonts/truetype/lato/Lato-Regular.ttf"


def fnt(s):
    return ImageFont.truetype(F, s)


W, PAD = 1200, 24
cover = Image.open(os.path.join(VK, "cover_b.png")).convert("RGB")
cw = W - 2 * PAD
cover_s = cover.resize((cw, round(cover.height * cw / cover.width)), Image.LANCZOS)

mock = cover.copy()
av = Image.open(os.path.join(VK, "avatar_b.png")).convert("RGB").resize((150, 150), Image.LANCZOS)
mask = Image.new("L", (150, 150), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 149, 149), fill=255)
mock.paste(av, (26, cover.height - 150 - 20), mask)
mock_s = mock.resize((cw, round(mock.height * cw / mock.width)), Image.LANCZOS)

avas = [Image.open(os.path.join(VK, f"avatar_{k}.png")).convert("RGB").resize((140, 140), Image.LANCZOS)
        for k in "abc"]

body = Image.new("RGB", (W, 1600), (250, 250, 250))
d = ImageDraw.Draw(body)
y = PAD
d.text((PAD, y), "«ЗАРЯНКА» — оформление ВК (2.5:1, без обрезки)", font=fnt(30), fill=(20, 20, 20))
y += 46
d.text((PAD, y), "Обложка 1920×768 (ровно формат ВК):", font=fnt(22), fill=(60, 60, 60))
y += 32
body.paste(cover_s, (PAD, y)); y += cover_s.height + 22
d.text((PAD, y), "Мок: аватар в левом-нижнем углу, композиция не перекрыта:", font=fnt(22), fill=(60, 60, 60))
y += 32
body.paste(mock_s, (PAD, y)); y += mock_s.height + 22
d.text((PAD, y), "Аватары 400×400 (B / A / C):", font=fnt(22), fill=(60, 60, 60))
y += 32
for i, a in enumerate(avas):
    body.paste(a, (PAD + i * 160, y))
y += 160
body = body.crop((0, 0, W, y + PAD))
out = os.path.join(REV, "review_20_vk_cover.png")
body.save(out, quality=92)
print("saved", out, body.size)
