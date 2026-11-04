# -*- coding: utf-8 -*-
from PIL import ImageFont
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
TXT = 'ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ'
f = ImageFont.truetype(GOTHIC, 46)
tw = f.getlength(TXT)
print('tw=%.0f' % tw)
w = int(tw + 98)
print('box x0=%d x1=%d  w=%d' % (1200 - w // 2, 1200 + w // 2, w))
