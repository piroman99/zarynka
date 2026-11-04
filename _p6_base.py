# -*- coding: utf-8 -*-
"""Вставка нашей лунной базы (арт из тизера) в марсианский кадр p6 — 0 ₽, вариант на глаз.

Иван 2026-11-04: «на кадр второй марсианской приделать бы нашу лунную базу с тизера».
Берём силуэт базы из `assets/gen/ok_space_station_0.jpg` (та же, что в тизере), вырезаем
по яркости над линией грунта y=552, перекрашиваем в марсианскую пыль и сажаем на горизонт
кадра p6. Ничего не утверждается: мастера не трогаем, результат — кандидаты в `assets/gen`.
"""
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets/final/prolog/p6.png')
ST = os.path.join(HERE, 'assets/gen/ok_space_station_0.jpg')
GEN = os.path.join(HERE, 'assets/gen')

base = Image.open(SRC).convert('RGB')
W, H = base.size

# --- вырезаем силуэт базы -------------------------------------------------
st = Image.open(ST).convert('RGB')
sw, sh = st.size
CROP = (0, 220, sw, 556)                  # полоса силуэта (грунт начинается с y=552)
cut = st.crop(CROP)
cim = np.asarray(cut).astype(np.float32)
lum = cim.mean(axis=2)

mask = (lum > 106).astype(np.uint8) * 255
mimg = Image.fromarray(mask, 'L')
mimg = mimg.filter(ImageFilter.MedianFilter(5))     # убираем крапины
mimg = mimg.filter(ImageFilter.MaxFilter(3))        # смыкаем тонкие щели
mimg = mimg.filter(ImageFilter.GaussianBlur(1.2))   # мягкая кромка
# низ базы — ровный: дорисуем к последней строке (иначе силуэт «висит»)
ma = np.asarray(mimg).copy()
ma[-8:, :] = np.maximum(ma[-8:, :], 235)
mimg = Image.fromarray(ma, 'L')

# --- перекраска в марсианскую пыль ---------------------------------------
warm = cim * np.array([1.07, 0.92, 0.82], dtype=np.float32)     # уводим серый в охру
dust = np.array([171, 122, 84], dtype=np.float32)
warm = warm * 0.78 + dust * 0.22
silhouette = Image.fromarray(np.clip(warm, 0, 255).astype(np.uint8), 'RGB')

VARIANTS = [
    ('A', 0.50, 470, 0.62, 2.2),   # дальний план: небольшая, в дымке
    ('B', 0.66, 505, 0.78, 1.3),   # средний план
    ('C', 0.82, 545, 0.90, 0.7),   # ближе, почти без дымки
]

out = []
for tag, wfrac, bottom, alpha, blur in VARIANTS:
    bw = int(W * wfrac)
    bh = int(silhouette.height * bw / silhouette.width)
    sil = silhouette.resize((bw, bh), Image.LANCZOS)
    msk = mimg.resize((bw, bh), Image.LANCZOS)
    if blur > 0:
        sil = sil.filter(ImageFilter.GaussianBlur(blur))
        msk = msk.filter(ImageFilter.GaussianBlur(blur))
    x = (W - bw) // 2
    y = bottom - bh
    # дымка: чем дальше (меньше alpha), тем сильнее подмешиваем цвет неба этой строки
    sky = np.asarray(base.crop((0, max(0, y), W, max(1, y + 6)))).astype(np.float32)
    skycol = sky.reshape(-1, 3).mean(axis=0)
    sa = np.asarray(sil).astype(np.float32) * alpha + skycol * (1 - alpha)
    sil = Image.fromarray(np.clip(sa, 0, 255).astype(np.uint8), 'RGB')
    canvas = base.copy()
    canvas.paste(sil, (x, y), msk.point(lambda v: int(v * alpha)))
    p = os.path.join(GEN, 'p6_base_var%s_0.png' % tag)
    canvas.save(p)
    out.append((tag, p, wfrac, bottom, alpha))
    print('%s: ширина %d px (%.0f%%), низ на y=%d, дымка %.2f, blur %.1f -> %s'
          % (tag, bw, wfrac * 100, bottom, alpha, blur, os.path.basename(p)))

# лист: источник + три варианта
from PIL import ImageDraw, ImageFont
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
cw, pad, lab = 1000, 14, 26
ch = int(round(cw * H / W))
rows = [('арт станции из тизера', ST), ('p6 как есть', SRC)] + \
       [('вариант %s — ширина %d%%, дымка %.2f' % (t, int(w * 100), a), p) for t, p, w, _, a in out]
Hc = (ch + lab + pad) * len(rows) + pad
cv = Image.new('RGB', (cw + 2 * pad, Hc), (14, 16, 22))
d = ImageDraw.Draw(cv)
y = pad
for labt, p in rows:
    im = Image.open(p).convert('RGB')
    im = im.resize((cw, ch), Image.LANCZOS) if im.size != (cw, ch) else im
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(52, 56, 68))
    d.text((pad, y + ch + 3), labt, fill=(216, 220, 228), font=f)
    y += ch + lab + pad
o = os.path.join(HERE, '_sat', 'sheet_p6_base.png')
cv.save(o)
print('лист', o, cv.size)
