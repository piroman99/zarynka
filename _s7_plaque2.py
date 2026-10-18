# -*- coding: utf-8 -*-
"""S7 — ТИХАЯ табличка на стене: варианты «потише» (Иван, 2026-10-18: «слишком заметная»).

Стену замерил по кадру assets/gen/s7b_gpt_a_0.png (1672x941):
  гладкая нейтральная плоскость x 0..98, y 0..525 (lum ~152, hue ~23, sat 0.15, grad ~2).
  В 2400x1350 это x 0..141.

Три варианта «потише»: меньше размер, ниже контраст, гравировка вместо красной эмали,
мягкая тень. Всё считается локально — 0 ₽.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
SS = 4

# стиль: box в 2400x1350, цвет корпуса, цвет букв, alpha корпуса, blur, тень
STYLES = {
    # A: небольшая плашка в тон стене (стена ≈ 162,146,136), тёмная гравировка без красного
    'a': dict(box=(14, 352, 110, 408), plate=(166, 156, 140), ink=(122, 112, 96),
              alpha=232, blur=0.7, shadow=(0, 0, 0, 52), sh_off=(2, 3), sh_blur=5,
              lines=('ТЫ НЕ', 'ПРОЙДЁШЬ!'), frame=None, screws=True, fill_h=0.38),
    # B: ещё мельче, одна строка
    'b': dict(box=(14, 356, 82, 392), plate=(164, 154, 139), ink=(128, 118, 102),
              alpha=228, blur=0.8, shadow=(0, 0, 0, 45), sh_off=(2, 2), sh_blur=4,
              lines=('ТЫ НЕ ПРОЙДЁШЬ',), frame=None, screws=False, fill_h=0.5),
    # C: прежний размер, но в тон стене и без красной эмали
    'c': dict(box=(8, 352, 136, 428), plate=(164, 155, 140), ink=(126, 116, 100),
              alpha=222, blur=0.9, shadow=(0, 0, 0, 55), sh_off=(3, 4), sh_blur=6,
              lines=('ТЫ НЕ', 'ПРОЙДЁШЬ!'), frame=None, screws=True, fill_h=0.38),
}


def _art(w, h, st):
    W, H = w * SS, h * SS
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pr, pg, pb = st['plate']
    # лёгкий вертикальный градиент патины
    for y in range(H):
        t = y / max(H - 1, 1)
        c = (int(pr - 6 + 12 * t), int(pg - 6 + 12 * t), int(pb - 6 + 12 * t))
        d.line([(0, y), (W, y)], fill=c + (st['alpha'],))

    # кромка: тонкая, светлая сверху, тёмная снизу
    e = max(1, SS // 2)
    d.line([(SS, SS), (W - SS, SS)], fill=(pr + 34, pg + 34, pb + 30, 150), width=e)
    d.line([(SS, SS), (SS, H - SS)], fill=(pr + 20, pg + 20, pb + 18, 110), width=e)
    d.line([(SS, H - SS), (W - SS, H - SS)], fill=(pr - 40, pg - 40, pb - 34, 150), width=e)

    if st['frame']:
        m = int(3 * SS)
        d.rectangle([m, m, W - m, H - m], outline=st['frame'], width=max(1, SS // 2))

    lines = st['lines']
    # кегль прямо из высоты плашки: две строки = 0.38 H каждая, одна = 0.5 H
    size = int(H * st.get('fill_h', 0.38))
    f = ImageFont.truetype(GOTHIC, size)
    avail = W - int(8 * SS)
    widest = max(d.textlength(t, font=f) for t in lines)
    if widest > avail:
        size = int(size * avail / widest)
        f = ImageFont.truetype(GOTHIC, size)
    lh = size * 1.08
    total = lh * len(lines)
    y = (H - total) / 2 - size * 0.05
    ir, ig, ib = st['ink']
    for t in lines:
        # гравировка: тень-углубление + светлая кромка снизу
        d.text((W / 2, y + max(1, SS // 2)), t, font=f, fill=(pr + 26, pg + 24, pb + 20, 190), anchor='ma')
        d.text((W / 2, y), t, font=f, fill=(ir, ig, ib, 255), anchor='ma')
        y += lh

    if st['screws']:
        r = max(1, int(1.0 * SS))
        m2 = int(2.6 * SS)
        for cx, cy in ((m2, m2), (W - m2, m2), (m2, H - m2), (W - m2, H - m2)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(pr - 34, pg - 32, pb - 28, 200))

    im = im.resize((w, h), Image.LANCZOS)
    if st['blur']:
        im = im.filter(ImageFilter.GaussianBlur(st['blur']))
    return im


def plaque(base, style='a'):
    st = STYLES[style]
    x0, y0, x1, y1 = st['box']
    w, h = x1 - x0, y1 - y0
    ox, oy = st['sh_off']
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([x0 + ox, y0 + oy, x1 + ox, y1 + oy], fill=st['shadow'])
    sh = sh.filter(ImageFilter.GaussianBlur(st['sh_blur']))
    base = Image.alpha_composite(base.convert('RGBA'), sh)
    art = _art(w, h, st)
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    layer.paste(art, (x0, y0), art)
    return Image.alpha_composite(base, layer).convert('RGB')
