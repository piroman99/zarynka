# -*- coding: utf-8 -*-
"""Композитор кадров новеллы: фон + спрайт + диалоговое окно + имя.

Используется и для превью (PNG), и позже для видео (кадры -> ffmpeg).
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "src")
ORIG = os.path.join(HERE, "assets", "orig")
OUT = os.path.join(HERE, "out")

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

RED = (220, 38, 38)
CREAM = (240, 236, 228)
DARK = (13, 17, 23)


def load(name, base=SRC):
    return Image.open(os.path.join(base, name)).convert("RGBA")


def cover(img, w=W, h=H, focus=(0.5, 0.5)):
    """scale to fill w×h, crop around focus."""
    iw, ih = img.size
    s = max(w / iw, h / ih)
    nw, nh = int(iw * s), int(ih * s)
    im = img.resize((nw, nh), Image.LANCZOS)
    x = int((nw - w) * focus[0]); y = int((nh - h) * focus[1])
    return im.crop((x, y, x + w, y + h))


def fit_height(img, h):
    s = h / img.height
    return img.resize((max(1, int(img.width * s)), int(h)), Image.LANCZOS)


def vignette(img, power=0.5):
    import numpy as np
    a = np.asarray(img.convert("RGB")).astype("float32")
    yy, xx = np.mgrid[0:img.height, 0:img.width].astype("float32")
    cx, cy = img.width / 2, img.height / 2
    d = ((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2
    m = np.clip(1 - power * np.clip(d ** 0.6 - 0.25, 0, None), 0, 1)
    out = a * m[:, :, None]
    r = Image.fromarray(out.astype("uint8"), "RGB")
    return r.convert("RGBA")


def scanlines(img, alpha=16, step=3, color=(0, 0, 0)):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, img.height, step):
        d.line([(0, y), (img.width, y)], fill=color + (alpha,))
    return Image.alpha_composite(img, ov)


def wrap(text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def dialogue_box(img, name, text, name_color=RED):
    d = ImageDraw.Draw(img, "RGBA")
    bx, by = 70, H - 268
    bw, bh = W - 140, 210
    # panel
    panel = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([0, 0, bw, bh], 18, fill=(9, 12, 18, 214), outline=(255, 255, 255, 26), width=1)
    img.alpha_composite(panel, (bx, by))
    # name tag
    if name:
        f = ImageFont.truetype(SANS_B, 30)
        nw = int(f.getlength(name)) + 46
        tag = Image.new("RGBA", (nw, 52), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag)
        td.rounded_rectangle([0, 0, nw - 1, 51], 13, fill=(20, 22, 28, 236), outline=name_color + (200,), width=2)
        td.text((23, 9), name, font=f, fill=name_color)
        img.alpha_composite(tag, (bx + 22, by - 26))
    # text
    f = ImageFont.truetype(SERIF, 30)
    lines = wrap(text, f, bw - 88)
    ty = by + 40
    for ln in lines[:5]:
        d.text((bx + 44, ty), ln, font=f, fill=CREAM)
        ty += 40
    return img


def title_card(bg, title, subtitle, by_line):
    img = cover(bg).convert("RGBA")
    img = vignette(img, 0.55)
    d = ImageDraw.Draw(img, "RGBA")
    ft = ImageFont.truetype(SERIF_B, 128)
    fs = ImageFont.truetype(SERIF, 30)
    fb = ImageFont.truetype(SANS, 22)
    tw = ft.getlength(title)
    d.text(((W - tw) / 2, 150), title, font=ft, fill=(245, 240, 230))
    d.line([(W / 2 - 180, 300), (W / 2 + 180, 300)], fill=RED + (200,), width=2)
    sw = fs.getlength(subtitle)
    d.text(((W - sw) / 2, 322), subtitle, font=fs, fill=(214, 208, 198))
    for i, ln in enumerate(by_line.split("\n")):
        w = fb.getlength(ln)
        d.text(((W - w) / 2, H - 150 + i * 30), ln, font=fb, fill=(150, 146, 140))
    return img


def sprite_frame(bg, sprite, name, text, sp_h=0.9, sp_x=0.72, flip=False, name_color=RED, scan=True):
    base = cover(bg).convert("RGBA")
    base = vignette(base, 0.5)
    if sprite is not None:
        sp = fit_height(sprite, int(H * sp_h))
        if flip:
            sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
        # soft drop shadow
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sh.paste((0, 0, 0, 120), (int(W * sp_x - sp.width // 2) + 8, H - sp.height + 12), sp)
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        base = Image.alpha_composite(base, sh)
        base.alpha_composite(sp, (int(W * sp_x - sp.width // 2), H - sp.height))
    if scan:
        base = scanlines(base, 12, 3)
    base = dialogue_box(base, name, text, name_color)
    return base


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    door = load("3029d614b3a2.png")          # дверь «Приёмная комиссия»
    wall = load("9f57530bfc6e.png")          # панорама «Марс — дело общее»
    kate_suit = load("caccf3b4ebc5.png")     # Зарянка в СКАФАНДРЕ — только космос/тренировки
    kate_suit2 = load("c66f332fa5c9.png")    # Зарянка в СКАФАНДРЕ (улыбка) — только космос
    kate_jump = load("za smile.png", base=ORIG)  # 2016: синий комбинезон — Земля, приёмная
    space = load("bg_space.png", base=os.path.join(HERE, "assets"))
    icon = load("icon_large.png", base=ORIG)

    frames = {}
    frames["01_title"] = title_card(space, "ЗАРЯНКА",
                                    "по рассказу Александра «Котобус» Горбова",
                                    "победитель номинации «Выбор читателей»\nконкурс «Будущее, до которого хочется дожить»")
    # Земля: синий комбинезон (оригинальный спрайт), НЕ скафандр
    frames["02_door"] = sprite_frame(door, kate_jump, None,
                                     "Приёмная комиссия. Весна. Лихнецкий откладывает папку — и поднимает глаза на следующего кандидата.")
    frames["03_kate"] = sprite_frame(door, kate_jump, "Екатерина Ивановна",
                                     "Здравствуйте, Сергей. Вот, пожалуйста, мои документы.")
    frames["04_wall"] = sprite_frame(wall, kate_jump, None,
                                     "Звёздный городок. Аллея космических достижений. Лозунг «Марс — дело общее!» облетел страну за неделю.")
    # Космос: скафандр (новый арт)
    frames["05_space_suit"] = sprite_frame(space, kate_suit, None,
                                           "Тренировки. Почти два года в космосе — это не шутка.", sp_h=0.92, sp_x=0.74)
    for k, im in frames.items():
        p = os.path.join(OUT, k + ".png")
        im.convert("RGB").save(p, quality=92)
        print("frame", p, im.size)
