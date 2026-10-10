# -*- coding: utf-8 -*-
"""Контрольный лист оформления ВК: обложка (десктоп), мобильный кроп, аватары + мок с аватаром."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VK = os.path.join(HERE, "assets", "vk")
REV = os.path.join(HERE, "assets", "review")
os.makedirs(REV, exist_ok=True)
F = "/usr/share/fonts/truetype/lato/Lato-Regular.ttf"
def fnt(s): return ImageFont.truetype(F, s)

W = 1200
PAD = 24
cover = Image.open(os.path.join(VK, "cover_b.png")).convert("RGB")
mob = Image.open(os.path.join(VK, "cover_b_mobile.png")).convert("RGB")

cw = W - 2 * PAD
cover_s = cover.resize((cw, round(cover.height * cw / cover.width)), Image.LANCZOS)
mob_s = mob.resize((cw, round(mob.height * cw / mob.width)), Image.LANCZOS)

# мок: обложка с аватаром в левом-нижнем углу (как рисует ВК)
mock = cover.copy()
av = Image.open(os.path.join(VK, "avatar_b.png")).convert("RGB").resize((190, 190), Image.LANCZOS)
mask = Image.new("L", (190, 190), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 189, 189), fill=255)
ring = Image.new("RGB", (202, 202), (255, 255, 255))
ring.paste(av, (6, 6), mask)
mock.paste(ring, (26, cover.height - 202))
mock_s = mock.resize((cw, round(mock.height * cw / mock.width)), Image.LANCZOS)

avas = [Image.open(os.path.join(VK, f"avatar_{k}.png")).convert("RGB").resize((150, 150), Image.LANCZOS)
        for k in "abc"]

rows = []
y = PAD
def label(txt):
    global y
    d.text((PAD, y), txt, font=fnt(24), fill=(30, 30, 30)); y += 34

body = Image.new("RGB", (W, 2000), (250, 250, 250))
d = ImageDraw.Draw(body)
d.text((PAD, y), "«ЗАРЯНКА» — оформление сообщества ВК", font=fnt(30), fill=(20, 20, 20)); y += 46
label("Обложка, десктоп 1590×400:")
body.paste(cover_s, (PAD, y)); y += cover_s.height + 20
label("Мобильная видимая зона 1196×400 (безопасная):")
body.paste(mob_s, (PAD, y)); y += mob_s.height + 20
label("Мок: как ВК кладёт аватар (левый-нижний угол) — контент не перекрыт:")
body.paste(mock_s, (PAD, y)); y += mock_s.height + 20
label("Аватары 400×400 (B / A / C):")
for i, a in enumerate(avas):
    body.paste(a, (PAD + i * 170, y))
y += 170
body = body.crop((0, 0, W, y + PAD))
out = os.path.join(REV, "review_19_vk.png")
body.save(out, quality=92)
print("saved", out, body.size)
