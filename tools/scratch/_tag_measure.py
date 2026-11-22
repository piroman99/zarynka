# -*- coding: utf-8 -*-
"""Проверка метки сцены (tag) в финальных PNG: влезает ли текст в чёрную плашку."""
from PIL import Image, ImageDraw, ImageFont

LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
d = ImageDraw.Draw(Image.new('RGB', (8, 8)))
for t in ('ПЛОЩАДЬ · ЛОЗУНГ', 'ЗАЛ · ВОПРОС', 'ВЕРХОВНЫЙ СОВЕТ', 'ПРОХОДНАЯ · ОЧЕРЕДЬ'):
    w = d.textlength(t, font=ImageFont.truetype(LATO_B, 30))
    box_w = 26 + len(t) * 15
    print('%-22r len=%d text=%.0f box=%d %s' % (t, len(t), w, box_w,
                                                'OK' if w <= box_w else 'ОБРЕЗКА'))
