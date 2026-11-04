# -*- coding: utf-8 -*-
"""Проверка, что головы спрайтов реально попали в кадр (не срезаны и не пустые)."""
import os
from PIL import Image, ImageStat
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '_sat')
# область головы в кадре 1920x1080 (по геометрии спрайтов)
REG = {
    'rec34_kate_head': ('sat_rec34.png', (1050, 40, 1390, 360)),
    'rec34_sergey_head': ('sat_rec34.png', (240, 40, 520, 330)),
    'rec16_kate_head': ('sat_rec16.png', (1050, 40, 1390, 360)),
    'star01_head': ('sat_star01.png', (740, 40, 930, 330)),
}
for nm, (f, box) in REG.items():
    im = Image.open(os.path.join(OUT, f)).convert('RGB').crop(box)
    st = ImageStat.Stat(im)
    print('%-20s std=%s mean=%s' % (nm, [round(v, 1) for v in st.stddev],
                                    [round(v, 1) for v in st.mean]))
