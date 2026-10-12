# -*- coding: utf-8 -*-
"""Кроп тулбара/навигации из скриншотов vn2 (проверка вида тумблеров и стрелок)."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')


def crop(name, box, out, scale=3):
    im = Image.open(os.path.join(REV, 'review_70_vn2_%s.png' % name)).convert('RGB')
    c = im.crop(box)
    c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
    c.save(os.path.join(REV, out))
    print(out, c.size)


# тулбар справа сверху
crop('auto_on', (820, 6, 1280, 74), 'review_70_vn2_peek_tools_auto.png')
crop('kate_sergey', (820, 6, 1280, 74), 'review_70_vn2_peek_tools_off.png')
# стрелка "назад" слева по центру
crop('kate_sergey', (0, 250, 120, 480), 'review_70_vn2_peek_prev.png')
# стрелка "далее" справа по центру
crop('kate_sergey', (1170, 250, 1280, 480), 'review_70_vn2_peek_next.png')

# сборка-полоска
tiles = ['review_70_vn2_peek_tools_auto.png', 'review_70_vn2_peek_tools_off.png',
         'review_70_vn2_peek_prev.png', 'review_70_vn2_peek_next.png']
ims = [Image.open(os.path.join(REV, t)).convert('RGB') for t in tiles]
W = max(i.width for i in ims); H = sum(i.height for i in ims)
sheet = Image.new('RGB', (W, H), (8, 10, 14))
y = 0
for i in ims:
    sheet.paste(i, (0, y)); y += i.height
sheet.save(os.path.join(REV, 'review_74_vn2_nav_tools.png'))
print('SHEET', sheet.size)
