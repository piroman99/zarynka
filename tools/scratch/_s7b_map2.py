import numpy as np
from PIL import Image

im = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
mx = a.max(2); mn = a.min(2)
lum = a.mean(2)
sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)

def hue():
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6,
                 np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h
hu = hue()

GW, GH = 48, 27
rows = []
for j in range(GH):
    line = ''
    for i in range(GW):
        sl = (slice(int(j*H/GH), int((j+1)*H/GH)), slice(int(i*W/GW), int((i+1)*W/GW)))
        L = lum[sl].mean(); S = sat[sl].mean(); HU = hu[sl].mean(); M = mx[sl].mean()
        if L < 55:
            c = '@'            # очень тёмно
        elif S < 0.13:
            c = '#' if L > 175 else ('=' if L > 120 else '-')   # нейтральное/камень
        elif HU < 22 or HU > 335:
            c = 'r'            # красное/кожа
        elif HU < 45:
            c = 'o'            # оранжевое/дерево/кожа-тёплое
        elif HU < 70:
            c = 'y'            # жёлтое/песок
        elif HU < 160:
            c = 'g'            # зелень
        elif HU < 260:
            c = 'c'            # голубое/небо
        else:
            c = 'v'
        line += c
    rows.append(line)

print('   ' + ''.join(str((i // 10) % 10) for i in range(GW)))
print('   ' + ''.join(str(i % 10) for i in range(GW)))
for j, row in enumerate(rows):
    print('%2d %s  y=%4d' % (j, row, int(j*H/GH)))
print('\n#/= нейтральный камень, = светлее, @ тень, g зелень, c небо, o/r кожа-тёплое, y песок')
print('cell = %.1f x %.1f px' % (W/GW, H/GH))
