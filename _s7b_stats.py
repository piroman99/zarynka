import numpy as np
from PIL import Image
import colorsys

im = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB')
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape

def hue_hist(name, y0, y1):
    r = a[int(y0*h):int(y1*h)].reshape(-1, 3) / 255.0
    mx = r.max(1); mn = r.min(1); v = mx; s = np.where(mx > 0, (mx-mn)/np.maximum(mx,1e-6), 0)
    d = np.maximum(mx-mn, 1e-6)
    rr, gg, bb = r[:,0], r[:,1], r[:,2]
    hue = np.where(mx == rr, ((gg-bb)/d) % 6, np.where(mx == gg, (bb-rr)/d + 2, (rr-gg)/d + 4)) * 60
    ok = (s > 0.12) & (v > 0.08)
    bins = [0,20,45,70,100,140,180,230,290,340,360]
    print('--', name, 'colored px %.2f' % ok.mean())
    for i in range(len(bins)-1):
        sel = ok & (hue >= bins[i]) & (hue < bins[i+1])
        print('    %3d-%3d°  %.3f' % (bins[i], bins[i+1], sel.mean()))
    print('    mean sat %.2f  mean val %.2f' % (s.mean(), v.mean()))

hue_hist('top 0-12%', 0.00, 0.12)
hue_hist('mid 30-45%', 0.30, 0.45)
hue_hist('low 70-100%', 0.70, 1.00)

# контраст/резкость
g = a.mean(2)
gy, gx = np.gradient(g)
print('mean |grad| %.2f' % np.hypot(gx, gy).mean())
