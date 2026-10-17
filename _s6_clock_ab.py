# -*- coding: utf-8 -*-
"""Электронное табло-часы (диегетическое): семь сегментов, тёмная панель, тёплое свечение.
Проба размещения на плашке S6-B — 3 кандидата, лист-выборка (0 ₽, без генерации)."""
import os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))

# сегменты: a верх, b верх-право, c низ-право, d низ, e низ-лево, f верх-лево, g середина
SEG = {
    '0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc',
    '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcfgd',
    ':': '',
}


def seg_poly(x, y, w, h, seg, t):
    """Полигон сегмента в рамке (x,y,w,h); t — толщина."""
    g = t * 0.42
    m = t / 2.0
    if seg == 'a':
        return [(x + m, y + m), (x + w - m, y + m), (x + w - m - t, y + t), (x + m + t, y + t)]
    if seg == 'd':
        return [(x + m + t, y + h - t), (x + w - m - t, y + h - t), (x + w - m, y + h - m), (x + m, y + h - m)]
    if seg == 'g':
        return [(x + m + t, y + h / 2 - g), (x + w - m - t, y + h / 2 - g),
                (x + w - m - t, y + h / 2 + g), (x + m + t, y + h / 2 + g)]
    if seg == 'f':
        return [(x + m, y + m), (x + t, y + t), (x + t, y + h / 2 - g), (x + m, y + h / 2 - g * 0.6)]
    if seg == 'b':
        return [(x + w - m, y + m), (x + w - t, y + t), (x + w - t, y + h / 2 - g),
                (x + w - m, y + h / 2 - g * 0.6)]
    if seg == 'e':
        return [(x + m, y + h / 2 + g * 0.6), (x + t, y + h / 2 + g), (x + t, y + h - t), (x + m, y + h - m)]
    if seg == 'c':
        return [(x + w - m, y + h / 2 + g * 0.6), (x + w - t, y + h / 2 + g),
                (x + w - t, y + h - t), (x + w - m, y + h - m)]
    return []


def draw_led_text(d, x, y, h, text, color, t_ratio=0.16):
    """Рисует текст семисегментными цифрами; возвращает ширину."""
    t = max(2, int(h * t_ratio))
    w = h * 0.56
    gap = h * 0.20
    cx = x
    for ch in text:
        if ch == ':':
            r = t * 0.75
            d.ellipse([cx + gap * 0.2, y + h * 0.28 - r, cx + gap * 0.2 + 2 * r, y + h * 0.28 + r], fill=color)
            d.ellipse([cx + gap * 0.2, y + h * 0.66 - r, cx + gap * 0.2 + 2 * r, y + h * 0.66 + r], fill=color)
            cx += gap + t * 1.2
            continue
        for s in SEG.get(ch, ''):
            d.polygon(seg_poly(cx, y, w, h, s, t), fill=color)
        cx += w + gap
    return cx - x - gap


def clock(base, box, text='06:07', color=(255, 96, 60)):
    """Панель-табло в box (x0,y0,x1,y1) с LED-цифрами и мягким свечением."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    pad = int(h * 0.16)
    # свечение позади
    glow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad],
                                           radius=int(h * 0.2), fill=color + (70,))
    glow = glow.filter(ImageFilter.GaussianBlur(int(h * 0.28)))
    base = Image.alpha_composite(base.convert('RGBA'), glow).convert('RGB')
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(h * 0.16), fill=(16, 17, 20))
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(h * 0.16), outline=(58, 60, 66), width=max(1, int(h * 0.05)))
    th = int(h * 0.52)
    tw = draw_led_text(d, 0, -1000, th, '00:00', color)  # измерить ширину
    x = x0 + (w - tw) / 2
    draw_led_text(d, x, y0 + (h - th) / 2, th, text, color)
    return base


def preview():
    src = os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')
    im = Image.open(src).convert('RGB').resize((2400, 1350), Image.LANCZOS)
    cands = [
        ('C1 · табло на будке', (1898, 322, 2108, 412)),
        ('C2 · на правой стойке ворот', (1428, 430, 1600, 512)),
        ('C3 · над турникетом', (1560, 596, 1790, 682)),
    ]
    out = []
    for label, box in cands:
        v = clock(im.copy(), box)
        crop = v.crop((max(0, box[0] - 260), max(0, box[1] - 180),
                       min(2400, box[2] + 260), min(1350, box[3] + 220)))
        out.append((label, v, crop))
        print(label, box)
    # лист
    W = 1300
    full = im.resize((W, int(1350 * W / 2400)), Image.LANCZOS)
    crops = [(lb, c.resize((W, int(c.height * W / c.width)), Image.LANCZOS)) for lb, _, c in out]
    pad = 18
    H = 8 + full.height + pad + sum(30 + c.height + pad for _, c in crops)
    sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
    from PIL import ImageFont
    f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 22)
    dd = ImageDraw.Draw(sheet)
    y = 8
    dd.text((pad, y), 'исходный кадр B (без часов)', font=f, fill=(232, 200, 140)); y += 30
    sheet.paste(full, (pad, y)); y += full.height + pad
    for lb, c in crops:
        dd.text((pad, y), lb, font=f, fill=(150, 190, 230)); y += 30
        sheet.paste(c, (pad, y)); y += c.height + pad
    p = os.path.join(HERE, 'assets', 'review', 'review_120_s6_clock_ab.png')
    sheet.save(p)
    print('sheet ->', os.path.relpath(p, HERE), sheet.size)


if __name__ == '__main__':
    preview()
