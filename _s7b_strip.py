import numpy as np
from PIL import Image, ImageFilter

im = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32)
mx = a.max(2); mn = a.min(2)
lum = a.mean(2)
sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
gL = np.asarray(im.convert('L')).astype(np.float32)
gy, gx = np.gradient(gL)
mag = np.hypot(gx, gy)

print('row  | lum/sat/grad по x 0..140 шагом 10')
for y in range(240, 420, 20):
    line = []
    for x in range(0, 140, 10):
        L = lum[y:y+10, x:x+10].mean()
        S = sat[y:y+10, x:x+10].mean()
        M = mag[y:y+10, x:x+10].mean()
        line.append('%3.0f/%.2f/%2.0f' % (L, S, M))
    print('y=%3d ' % y + ' '.join(line))
print()
print('профиль гладкости по x (усреднение y 250..420):')
for x in range(0, 200, 10):
    print('  x %3d..%3d  lum %3.0f  sat %.2f  grad %4.1f' % (
        x, x+10, lum[250:420, x:x+10].mean(), sat[250:420, x:x+10].mean(),
        mag[250:420, x:x+10].mean()))
