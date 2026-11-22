import numpy as np
from PIL import Image

im = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB')
a = np.asarray(im).astype(np.float32)
H, W, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
mx = a.max(2); mn = a.min(2)
d = np.maximum(mx - mn, 1e-6)
hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
lum = a.mean(2)

print('вертикальный профиль полосы x 20..90:')
for y in range(0, 700, 25):
    sl = (slice(y, y + 25), slice(20, 90))
    print('  y %3d..%3d  lum %5.1f  hue %5.1f  sat %.2f' % (
        y, y+25, lum[sl].mean(), hue[sl].mean(),
        ((mx[sl]-mn[sl])/np.maximum(mx[sl],1)).mean()))

print('\nгоризонтальный профиль (x 0..110) на разных y:')
for y in (120, 260, 400, 520):
    row = []
    for x in range(0, 110, 15):
        row.append('%4.0f' % lum[y:y+12, x:x+15].mean())
    print('  y %3d: %s' % (y, ' '.join(row)))
