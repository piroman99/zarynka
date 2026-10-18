import numpy as np
from PIL import Image

im = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB')
W, H = im.size
g = np.asarray(im.convert('L')).astype(np.float32)

# усреднение по блокам в карту 64x36
GW, GH = 64, 36
bw, bh = W / GW, H / GH
rows = []
for j in range(GH):
    line = ''
    for i in range(GW):
        b = g[int(j*bh):int((j+1)*bh), int(i*bw):int((i+1)*bw)]
        v = b.mean()
        line += ' ' if v < 40 else '.' if v < 70 else ':' if v < 100 else '-' if v < 130 else \
                '=' if v < 160 else '+' if v < 190 else '*' if v < 215 else '#'
    rows.append(line)

print('   ' + ''.join(str((i // 10) % 10) for i in range(GW)))
print('   ' + ''.join(str(i % 10) for i in range(GW)))
for j, r in enumerate(rows):
    print('%2d %s  y=%4d' % (j, r, int(j*bh)))
print()
print('block px = %.1f x %.1f' % (bw, bh))

# локальная «гладкость» (низкий градиент) — кандидаты под плоскую стену
gy, gx = np.gradient(g)
mag = np.hypot(gx, gy)
GW2, GH2 = 32, 18
rows = []
for j in range(GH2):
    line = ''
    for i in range(GW2):
        b = mag[int(j*H/GH2):int((j+1)*H/GH2), int(i*W/GW2):int((i+1)*W/GW2)]
        m = b.mean()
        line += '#' if m < 3 else '+' if m < 6 else '-' if m < 10 else ':' if m < 16 else '.'
    rows.append(line)
print('\nSMOOTH map (# = очень гладко):')
print('   ' + ''.join(str((i // 10) % 10) for i in range(GW2)))
print('   ' + ''.join(str(i % 10) for i in range(GW2)))
for j, r in enumerate(rows):
    print('%2d %s  y=%4d' % (j, r, int(j*H/GH2)))
