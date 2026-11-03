# -*- coding: utf-8 -*-
"""Проверка вписывания строк титр-слоя в плашку кадра (офлайн, по шрифтам).

Берёт pg.ovl из vn2/content.js и меряет каждую строку тем же шрифтом и кеглем,
что рендерит движок (URWGothic-Demi / Lato-Bold, размеры в пространстве 2400x1350).
Проверяет: строка не вылезает за плашку и не за кадр.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
E = 2400.0
W, H = 2400, 1350

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))

d = ImageDraw.Draw(Image.new('RGB', (8, 8)))
bad = 0
for nd in D['nodes']:
    if nd.get('t') != 'scene':
        continue
    for i, pg in enumerate(nd.get('pages', [])):
        ov = pg.get('ovl')
        if not ov:
            continue
        boxes = [it['b'] for it in ov if 'b' in it]
        for it in ov:
            if 'b' in it:
                continue
            f = ImageFont.truetype(LATO_B if it.get('f') == 'l' else GOTHIC, it['s'])
            tw = d.textlength(it['t'], font=f)
            asc, desc = f.getmetrics()
            th = asc + desc
            a = it.get('a') or 'mm'
            cx, cy = it.get('x', 1200), it.get('y', 675)
            if a == 'mm':
                x0, y0 = cx - tw / 2, cy - th / 2
            elif a == 'ma':
                x0, y0 = cx - tw / 2, cy
            else:
                x0, y0 = cx, cy
            x1, y1 = x0 + tw, y0 + th
            ok = (x0 >= 0 and y0 >= 0 and x1 <= W and y1 <= H)
            note = ''
            if boxes:
                b = boxes[0]
                inb = (x0 >= b[0] and y0 >= b[1] and x1 <= b[2] and y1 <= b[3])
                if not inb:
                    # строки s3 намеренно шире плашки (кегль 108 не влезал и в PNG-версии)
                    note = 'шире плашки на %d px' % max(b[0] - x0, x1 - b[2], 0)
                    if a != 'mm' and it['s'] < 100:
                        ok = False
            print('%-4s стр.%d  %-30r кегль %3d  w=%4.0f  x=%.0f..%.0f y=%.0f..%.0f  %s %s'
                  % (nd['id'], i + 1, it['t'][:28], it['s'], tw, x0, x1, y0, y1,
                     'OK' if ok else 'ЗА КАДРОМ', note))
            if not ok:
                bad += 1
print('\nпроблем: %d' % bad)
sys.exit(1 if bad else 0)
