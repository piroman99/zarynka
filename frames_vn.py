# -*- coding: utf-8 -*-
"""Собирает VN-кадр: фон + спрайт(ы) + окно диалога с именем и текстом."""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 1672, 941


def f(path, sz):
    return ImageFont.truetype(path, sz)


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def place_sprite(canvas, sprite_path, scale_h=0.92, cx=0.63):
    sp = Image.open(sprite_path).convert("RGBA")
    th = int(H * scale_h)
    tw = int(sp.width * th / sp.height)
    sp = sp.resize((tw, th), Image.LANCZOS)
    x = int(W * cx - tw / 2)
    y = H - th + int(H * 0.02)
    # мягкая тень под персонажем
    sh = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 90), (0, 0), sp.split()[-1])
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    canvas.alpha_composite(sh, (x + 8, y + 8))
    canvas.alpha_composite(sp, (x, y))


def dialog(canvas, name, text, bg=None):
    d = ImageDraw.Draw(canvas, "RGBA")
    box_h = int(H * 0.30)
    y0 = H - box_h - int(H * 0.03)
    x0, x1 = int(W * 0.05), int(W * 0.95)
    d.rounded_rectangle([x0, y0, x1, y0 + box_h], radius=22,
                        fill=(12, 14, 20, 205), outline=(220, 60, 60, 230), width=3)
    nf, tf = f(FONTB, 34), f(FONT, 32)
    # плашка имени
    nw = int(d.textlength(name, font=nf)) + 44
    d.rounded_rectangle([x0 + 26, y0 - 26, x0 + 26 + nw, y0 + 26], radius=14,
                        fill=(220, 60, 60, 245))
    d.text((x0 + 48, y0 - 16), name, font=nf, fill=(255, 255, 255))
    lines = wrap(d, text, tf, (x1 - x0) - 80)
    ty = y0 + 56
    for ln in lines[:5]:
        d.text((x0 + 40, ty), ln, font=tf, fill=(238, 238, 242))
        ty += 44


def frame(bg, out, name=None, text=None, sprites=None):
    cv = Image.open(bg).convert("RGBA").resize((W, H), Image.LANCZOS)
    for s, cx, sc in (sprites or []):
        place_sprite(cv, s, scale_h=sc, cx=cx)
    if text:
        dialog(cv, name or "", text)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cv.convert("RGB").save(out, "PNG")
    print("saved", os.path.relpath(out, HERE), cv.size)
    return out


S = os.path.join(HERE, "assets/sprites")
BG = os.path.join(HERE, "assets/gen/bg_reception_vn_0.png")

if __name__ == "__main__":
    frame(BG, os.path.join(HERE, "out/vn_scene01_a.png"),
          name="Екатерина Ивановна",
          text="— Никто за вас работать не будет. Если хотите чего-то добиться — работайте.",
          sprites=[(os.path.join(S, "kate_overalls.png"), 0.63, 0.92)])
