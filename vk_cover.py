# -*- coding: utf-8 -*-
"""Оформление сообщества «Зарянка» ВК, v3.

УРОК: ВК хранит обложку в пропорции 2.5:1 (1920×768, 1080×432, …) и из загруженной
картинки берёт ЛЕВУЮ часть 2.5:1. Отдавали 1590×400 (~4:1) -> ВК резал правую часть
(заголовок «уезжал»). Решение: отдавать сразу 2.5:1 (1920×768) — тогда обрезки нет.

Правка заказчика №2: логотип «лёг грязно» -> бейдж вырезается ровно по медальону
(без белого фона) со сглаженным (supersampled + feathered) краем и мягкой тенью.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
VK = os.path.join(HERE, "assets", "vk")
os.makedirs(VK, exist_ok=True)

CW, CH = 1920, 768          # 2.5:1 — ровно то, что хранит ВК
K = CH / 400.0              # масштаб от базовой вёрстки 400px
SS = 4

CREAM = (240, 233, 219)
DIM = (180, 172, 158)
RED = (206, 68, 62)
GOLD = (214, 178, 92)


def font(path, sz):
    return ImageFont.truetype(path, int(sz))


def cyr_ok(path):
    try:
        return font(path, 40).getmask("Я").size[0] > 1
    except Exception:
        return False


def pick(cands):
    for c in cands:
        if os.path.exists(c) and cyr_ok(c):
            return c
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


FT = pick(["/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf",
           "/usr/share/fonts/truetype/lato/Lato-Black.ttf",
           "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"])
FB = pick(["/usr/share/fonts/truetype/lato/Lato-Medium.ttf",
           "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
print("fonts:", os.path.basename(FT), "/", os.path.basename(FB))


def detect_disc(im):
    W, H = im.size
    px = im.load()
    xs, ys = [], []
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            r, g, b = px[x, y]
            if (max(r, g, b) - min(r, g, b) > 14) or (r + g + b) / 3 < 228:
                xs.append(x); ys.append(y)
    if not xs:
        return W // 2, H // 2, min(W, H) // 2
    return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2,
            ((max(xs) - min(xs)) + (max(ys) - min(ys))) / 4)


def make_badge(logo_path, D, feather=2.4):
    """медальон в круглом бейдже: вырез ровно по диску, AA + мягкий край."""
    im = Image.open(logo_path).convert("RGB")
    cx, cy, R = detect_disc(im)
    R *= 0.992                     # остаться ВНУТРИ медальона
    box = (int(cx - R), int(cy - R), int(cx + R), int(cy + R))
    crop = im.crop(box).convert("RGBA").resize((D, D), Image.LANCZOS)
    m_big = Image.new("L", (D * SS, D * SS), 0)
    ImageDraw.Draw(m_big).ellipse((0, 0, D * SS - 1, D * SS - 1), fill=255)
    mask = m_big.resize((D, D), Image.LANCZOS)
    if feather:
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
    crop.putalpha(mask)
    return crop


def tracked(d, text, fnt, track):
    return sum(d.textlength(c, font=fnt) for c in text) + track * max(0, len(text) - 1)


def draw_tracked(d, xy, text, fnt, track, fill):
    x, y = int(xy[0]), int(xy[1])
    for c in text:
        d.text((x, y), c, font=fnt, fill=fill)
        x += d.textlength(c, font=fnt) + track


def cover_bg():
    bg = Image.open(os.path.join(GEN, "ok_x_ship_dock_0.jpg")).convert("RGB")
    r = max(CW / bg.width, CH / bg.height)
    bg = bg.resize((round(bg.width * r), round(bg.height * r)), Image.LANCZOS)
    x = (bg.width - CW) // 2
    y = (bg.height - CH) // 2
    bg = bg.crop((x, y, x + CW, y + CH))
    bg = Image.eval(bg, lambda v: int(v * 0.5))
    bg = Image.blend(bg, Image.new("RGB", (CW, CH), (9, 11, 16)), 0.30)
    grad = Image.new("L", (CW, 1))
    for i in range(CW):
        t = abs(i - CW / 2) / (CW / 2)
        grad.putpixel((i, 0), int(80 * (1 - t) ** 1.7))
    grad = grad.resize((CW, CH))
    return Image.composite(Image.new("RGB", (CW, CH), (6, 7, 10)), bg, grad)


def make_cover(logo_name, out_name):
    im = cover_bg().convert("RGBA")
    d = ImageDraw.Draw(im)

    f1 = font(FT, 104 * K)
    f2 = font(FB, 38 * K)
    f3 = font(FB, 25 * K)
    track1 = int(8 * K)
    title, sub = "ЗАРЯНКА", "визуальная новелла"
    auth = "по рассказу Александра «Котобус» Горбова"

    w1 = tracked(d, title, f1, track1)
    w2 = tracked(d, sub, f2, int(5 * K))
    w3 = d.textlength(auth, font=f3)
    tw = max(w1, w2, w3)

    D = int(210 * K)
    gap = int(56 * K)
    block_w = int(D + gap + tw)
    bx = int((CW - block_w) // 2)
    by = int((CH - D) // 2)
    tx = int(bx + D + gap)

    badge = make_badge(os.path.join(GEN, logo_name), D, feather=2.4)
    sh = Image.new("RGBA", (D + 80, D + 80), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", (D, D), (0, 0, 0, 175)), (40, 46), badge.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(int(16 * K)))
    im.alpha_composite(sh, (bx - 40, by - 40))
    im.alpha_composite(badge, (bx, by))

    h1 = f1.getbbox(title)[3] - f1.getbbox(title)[1]
    h2 = f2.getbbox(sub)[3] - f2.getbbox(sub)[1]
    h3 = f3.getbbox(auth)[3] - f3.getbbox(auth)[1]
    gapA, gapB = int(26 * K), int(24 * K)
    total = int(h1 + gapA + 3 * K + gapB + h2 + 20 * K + h3)
    y = int((CH - total) // 2)
    draw_tracked(d, (tx, y), title, f1, track1, CREAM)
    y += int(h1 + gapA)
    d.line((tx, y, tx + int(min(w1, tw)), y), fill=GOLD + (230,), width=max(2, int(3 * K)))
    y += int(3 * K + gapB)
    draw_tracked(d, (tx, y), sub, f2, int(5 * K), RED)
    y += int(h2 + 20 * K)
    d.text((tx, y), auth, font=f3, fill=DIM)

    im.convert("RGB").save(os.path.join(VK, out_name), quality=95)
    print("cover:", out_name, im.size)


def make_avatar(logo_name, out_name, D=360):
    canvas = 400
    av = Image.new("RGBA", (canvas, canvas), (255, 255, 255, 0))
    b = make_badge(os.path.join(GEN, logo_name), D, feather=2.4)
    av.alpha_composite(b, ((canvas - D) // 2, (canvas - D) // 2))
    av.convert("RGB").save(os.path.join(VK, out_name), quality=95)
    print("avatar:", out_name)


for k, name in (("a", "logo_a_0.jpg"), ("b", "logo_b_0.jpg"), ("c", "logo_c_0.jpg")):
    make_cover(name, f"cover_{k}.png")
    make_avatar(name, f"avatar_{k}.png")
print("done")
