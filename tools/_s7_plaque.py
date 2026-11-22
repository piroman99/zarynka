# -*- coding: utf-8 -*-
"""Диегетическая табличка на стене у приёмной (S7 v2, правка Ивана 2026-10-18:
«табличку как-то на стену тихонечко задвинуть не получится?»).

Геометрия стены замерена по кадру assets/gen/s7b_gpt_a_0.png (1672x941):
  гладкая нейтральная плоскость x 0..98, y 0..525 (lum ~152, hue ~23, grad ~2),
  справа от x=100 — резкая кромка (grad 29) и листва.
В пространстве сборки 2400x1350 это x 0..141; табличка ставится x 14..134,
y 350..444 — середина стены, выше подстрочника и ниже метки кадра.
Текст — «ТЫ НЕ / ПРОЙДЁШЬ!» тёмно-красным по эмали; читается при внимательном
взгляде, в общем плане это тихая железка на стене.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'

BOX = (8, 352, 136, 428)       # 128 x 76 в 2400x1350 — эмалевая плашка на стене
SS = 4                          # суперсэмплинг


def _plate_art(w, h, ss=SS):
    W, H = w * ss, h * ss
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # корпус эмали с вертикальным градиентом (сверху чуть темнее — патина)
    for y in range(H):
        t = y / max(H - 1, 1)
        c = (int(196 + 16 * t), int(188 + 15 * t), int(170 + 16 * t))
        d.line([(0, y), (W, y)], fill=c + (255,))

    # фаска: тёмная внешняя кромка + светлый блик сверху/слева
    d.rectangle([0, 0, W - 1, H - 1], outline=(96, 84, 68, 255), width=max(1, ss))
    d.line([(ss, ss), (W - ss, ss)], fill=(255, 250, 236, 200), width=max(1, ss // 2))
    d.line([(ss, ss), (ss, H - ss)], fill=(255, 250, 236, 150), width=max(1, ss // 2))
    d.line([(ss, H - ss), (W - ss, H - ss)], fill=(120, 104, 82, 170), width=max(1, ss // 2))

    # внутренняя рамка тёмно-красным
    m = int(4 * ss)
    d.rectangle([m, m, W - m, H - m], outline=(150, 46, 38, 235), width=max(1, int(1.4 * ss)))

    # текст: две строки, кегль подбирается под ширину
    lines = ['ТЫ НЕ', 'ПРОЙДЁШЬ!']
    avail = W - int(16 * ss)
    size = int(8 * ss)
    while True:
        f = ImageFont.truetype(GOTHIC, size)
        if max(d.textlength(t, font=f) for t in lines) > avail or size > H // 2:
            break
        size += 1
    size -= 1
    f = ImageFont.truetype(GOTHIC, size)
    print('   plaque: box %dx%d, font %.1f px (кегль в 2400 = %.1f)' % (w, h, size / ss, size / ss))
    lh = size * 1.06
    total = lh * len(lines)
    y = (H - total) / 2 - size * 0.06
    for t in lines:
        d.text((W / 2, y), t, font=f, fill=(146, 40, 34, 255), anchor='ma')
        y += lh

    # винты по углам
    r = max(2, int(1.6 * ss))
    for cx, cy in ((m + 2 * ss, m + 2 * ss), (W - m - 2 * ss, m + 2 * ss),
                   (m + 2 * ss, H - m - 2 * ss), (W - m - 2 * ss, H - m - 2 * ss)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 112, 96, 255))
        d.ellipse([cx - r, cy - r, cx, cy], fill=(214, 208, 190, 200))

    im = im.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.55))
    return im


def plaque(base, box=BOX):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0

    # контактная тень: смещена вправо-вниз, размыта, плотнее у кромки
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([x0 + 4, y0 + 6, x1 + 4, y1 + 6], fill=(18, 14, 10, 130))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    base = Image.alpha_composite(base.convert('RGBA'), sh)

    art = _plate_art(w, h)
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    layer.paste(art, (x0, y0), art)
    return Image.alpha_composite(base, layer).convert('RGB')
