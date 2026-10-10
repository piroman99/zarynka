# -*- coding: utf-8 -*-
"""Оформление сообщества «Зарянка» ВК: обложка 1590x400 + аватар 400x400 (+мобильный кроп).
Пишет в assets/vk/. Ничего не тратит (локальный PIL).
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
VK = os.path.join(HERE, "assets", "vk")
os.makedirs(VK, exist_ok=True)

CW, CH = 1590, 400          # обложка (десктоп)
MW = 1196                   # мобильная видимая зона (по центру)
AIN = 400                   # аватар (квадрат, показывается кругом)

CREAM = (240, 234, 222)
DIM = (176, 168, 154)
RED = (200, 60, 60)

def font(path, sz):
    return ImageFont.truetype(path, sz)

def cyr_ok(path):
    try:
        f = font(path, 40)
        m = f.getmask("Я")
        return m.size[0] > 1
    except Exception:
        return False

CAND_TITLE = [
    "/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf",
    "/usr/share/fonts/truetype/lato/Lato-Black.ttf",
    "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
CAND_BODY = [
    "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",
    "/usr/share/fonts/truetype/lato/Lato-Medium.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def pick(cands):
    for c in cands:
        if os.path.exists(c) and cyr_ok(c):
            return c
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

FT = pick(CAND_TITLE)
FB = pick(CAND_BODY)
print("title font:", os.path.basename(FT), "| body:", os.path.basename(FB))

def cover_crop(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def circle(im, size):
    """взять центральный квадрат, привести к size, вырезать круг с прозрачностью."""
    s = min(im.width, im.height)
    im = im.crop(((im.width - s) // 2, (im.height - s) // 2,
                  (im.width - s) // 2 + s, (im.height - s) // 2 + s)).convert("RGBA")
    im = im.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    im.putalpha(mask)
    return im

def tracked(d, text, fnt, track):
    """ширина текста с межбуквенным интервалом."""
    w = 0
    for ch in text:
        w += d.textlength(ch, font=fnt) + track
    return w - track if text else 0

def draw_tracked(d, xy, text, fnt, track, fill):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + track

def make_cover(logo_name, out_name):
    bg = Image.open(os.path.join(GEN, "ok_x_ship_dock_0.jpg")).convert("RGB")
    bg = cover_crop(bg, CW, CH)
    # затемнить + лёгкая радиальная «виньетка», чтобы текст читался
    bg = Image.eval(bg, lambda v: int(v * 0.52))
    dark = Image.new("RGB", (CW, CH), (10, 12, 17))
    bg = Image.blend(bg, dark, 0.28)
    # мягкое затемнение к центру
    grad = Image.new("L", (CW, 1))
    for x in range(CW):
        t = abs(x - CW / 2) / (CW / 2)
        grad.putpixel((x, 0), int(70 * (1 - t) ** 1.6))
    grad = grad.resize((CW, CH))
    bg = Image.composite(Image.new("RGB", (CW, CH), (6, 7, 10)), bg, grad)

    im = bg.convert("RGBA")
    d = ImageDraw.Draw(im)

    # --- логотип-бейдж слева от названия ---
    badge = circle(Image.open(os.path.join(GEN, logo_name)).convert("RGB"), 168)
    bx, by = 356, (CH - badge.height) // 2
    # золотое свечение
    glow = Image.new("RGBA", (badge.width + 40, badge.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((20, 20, badge.width + 20, badge.height + 20),
                                 fill=(212, 175, 55, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(16))
    im.alpha_composite(glow, (bx - 20, by - 20))
    im.alpha_composite(badge, (bx, by))

    f1 = font(FT, 122)
    f2 = font(FB, 35)
    f3 = font(FB, 25)
    tx = bx + badge.width + 54
    # название (с межбуквенным интервалом)
    t_track = 7
    tw = tracked(d, "ЗАРЯНКА", f1, t_track)
    draw_tracked(d, (tx, 84), "ЗАРЯНКА", f1, t_track, CREAM)
    # линия-разделитель
    d.line((tx, 228, tx + min(tw, 560), 228), fill=(212, 175, 55, 220), width=3)
    draw_tracked(d, (tx, 246), "визуальная новелла", f2, 5, RED)
    d.text((tx, 302), "по рассказу Александра «Котобус» Горбова", font=f3, fill=DIM)

    out = os.path.join(VK, out_name)
    im.convert("RGB").save(out, quality=95)
    # мобильная видимая зона
    mob = im.convert("RGB").crop(((CW - MW) // 2, 0, (CW - MW) // 2 + MW, CH))
    mob.save(os.path.join(VK, out_name.replace(".png", "_mobile.png")), quality=95)
    print("cover:", out_name, im.size)
    return out

def make_avatar(logo_name, out_name):
    a = circle(Image.open(os.path.join(GEN, logo_name)).convert("RGB"), AIN)
    bg = Image.new("RGB", (AIN, AIN), (10, 12, 17))
    bg.paste(a, (0, 0), a)
    out = os.path.join(VK, out_name)
    bg.save(out, quality=95)
    print("avatar:", out_name, bg.size)

make_cover("logo_b_0.jpg", "cover_b.png")
make_cover("logo_a_0.jpg", "cover_a.png")
make_cover("logo_c_0.jpg", "cover_c.png")
make_avatar("logo_b_0.jpg", "avatar_b.png")
make_avatar("logo_a_0.jpg", "avatar_a.png")
make_avatar("logo_c_0.jpg", "avatar_c.png")
print("done")
