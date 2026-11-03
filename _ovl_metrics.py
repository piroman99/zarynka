# -*- coding: utf-8 -*-
"""Замеры под титр-слой: кегли/ширины строк s3/s4/s5 в пространстве 2400x1350."""
from PIL import Image, ImageDraw, ImageFont

GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
img = Image.new('RGB', (10, 10))
d = ImageDraw.Draw(img)


def w(t, p, s):
    return d.textlength(t, font=ImageFont.truetype(p, s))


def h(t, p, s):
    f = ImageFont.truetype(p, s)
    b = f.getbbox(t)
    return b


print('--- s3 (плашка 620,330,1780,1010) ---')
for t, p, s in [('«МАРС —', GOTHIC, 108), ('ДЕЛО ОБЩЕЕ?»', GOTHIC, 108),
                ('«ОБЩЕЕ!»', GOTHIC, 86), ('а что же обычных людей нет?', LATO_B, 52)]:
    print('%-28r w=%.0f bbox=%s' % (t, w(t, p, s), h(t, p, s)))

print('--- s4: подгон под 94% экрана ТВ (733..1650, ширина 917) ---')
TXT = 'а что же обычных людей нет?'
TARGET = int((1650 - 733) * 0.94)
size = 40
while w(TXT, LATO_B, size) < TARGET:
    size += 1
tw = w(TXT, LATO_B, size)
print('size=%d tw=%.0f target=%d' % (size, tw, TARGET))
print('bbox=%s' % (h(TXT, LATO_B, size),))

print('--- s5: чип «ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ» GOTHIC 46 ---')
for t in ['2 МЕСТА «С УЛИЦЫ»', 'ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ', 'ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ'.replace('«', '')]:
    print('%-30r w46=%.0f' % (t, w(t, GOTHIC, 46)))
print('--- размер под ширину чипа 720 при 94%%: ---')
t = 'ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ'
s = 46
while w(t, GOTHIC, s) > int(720 * 1.0):
    s -= 1
print('влезает в 720 при size=%d (w=%.0f)' % (s, w(t, GOTHIC, s)))
