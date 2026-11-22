import numpy as np, os
from PIL import Image, ImageDraw, ImageFilter

im = Image.open('assets/final/prolog/s7.png').convert('RGB')
W, H = im.size
s = W / 2400.0
x0, y0, x1, y1 = [int(round(v * s)) for v in (14, 350, 134, 444)]
print('final', (W, H), 'box in final', (x0, y0, x1, y1))
a = np.asarray(im.convert('L')).astype(np.float32)
reg = a[y0:y1, x0:x1]
print('plate lum min %.0f max %.0f mean %.0f std %.1f' % (reg.min(), reg.max(), reg.mean(), reg.std()))

step = 1
for yy in range(0, reg.shape[0], step):
    line = ''
    for xx in range(0, reg.shape[1], step):
        v = reg[yy, xx]
        line += '#' if v < 110 else '+' if v < 150 else '-' if v < 185 else '=' if v < 215 else '.'
    print(line)

# маска виньетки в этом месте
mask = Image.new('L', (2400, 1350), 0)
ImageDraw.Draw(mask).ellipse([-2400*0.22, -1350*0.30, 2400*1.22, 1350*1.30], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(2400 // 10))
m = np.asarray(mask).astype(np.float32)
v = 255 - (255 - m) * 0.75
print('vignette factor at plate: %.0f..%.0f (mean %.0f)' % (
    v[350:444, 14:134].min(), v[350:444, 14:134].max(), v[350:444, 14:134].mean()))
