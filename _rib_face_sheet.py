import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')
GOTH = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(src, '_znak3d.py', 'exec'), ns)
render = ns['render']


def macro(im):
    arr = np.asarray(im)
    fg = (np.abs(arr.astype(int) - np.array([6, 8, 18])).sum(axis=2) > 24)
    ys, xs = np.where(fg)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    c = im.crop((max(0, x0 - 30), max(0, y0 - 8), min(1280, x1 + 30), min(1280, y1 + 8)))
    sc = 560 / c.height
    return c.resize((max(1, int(c.width * sc)), 560), Image.LANCZOS), (x1 - x0 + 1)


faces = [None, 3, 4]
panels = []
for face in faces:
    im = render(90) if face is None else render(90, rib_face=face)
    m, w = macro(im)
    panels.append((m, 'rib_face=%s' % face))
W = sum(p[0].width for p in panels) + 40 * (len(panels) + 1)
H = 560 + 150
sheet = Image.new('RGB', (W, H), (16, 17, 22))
d = ImageDraw.Draw(sheet)
d.text((20, 16), 'При 90° (ребро) — на какой грани видна гравировка?', font=ImageFont.truetype(GOTH, 30), fill=(226, 186, 104))
x = 40
for m, cap in panels:
    sheet.paste(m, (x, 90))
    d.text((x, 90 + 560 + 8), cap, font=ImageFont.truetype(LATO_B, 22), fill=(240, 236, 228))
    x += m.width + 40
sheet.save(os.path.join(REV, 'review_62_rib_face.png'))
print('saved', sheet.size)
