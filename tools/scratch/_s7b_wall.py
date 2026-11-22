import numpy as np
from PIL import Image, ImageFilter

im = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
mx = a.max(2); mn = a.min(2)
lum = a.mean(2)
sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)

def box(mask, radius):
    img = Image.fromarray((mask * 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.BoxBlur(radius))).astype(np.float32) / 255.0

gL = np.asarray(im.convert('L')).astype(np.float32)
gy, gx = np.gradient(gL)
mag = np.hypot(gx, gy)
mag_s = box(mag / 255.0, 4) * 255.0

skin = (r > 95) & (g > 40) & (b > 20) & (r > g + 12) & (r > b + 18) & (sat > 0.18) & (lum > 55)
skin_s = box(skin.astype(np.float32), 7) > 0.12

cand = (mag_s < 4.5) & (sat < 0.26) & (lum > 78) & (lum < 205) & ~skin_s
cand[: int(H * 0.06)] = False
cand[int(H * 0.78):] = False
cand_s = box(cand.astype(np.float32), 12) > 0.88
print('candidate share %.3f' % cand_s.mean())

# связные области: BFS по сетке 4 px для скорости
step = 4
small = cand_s[::step, ::step]
sh, sw = small.shape
seen = np.zeros_like(small, dtype=bool)
regions = []
for y in range(sh):
    for x in range(sw):
        if not small[y, x] or seen[y, x]:
            continue
        stack = [(y, x)]
        seen[y, x] = True
        pts = []
        while stack:
            cy, cx = stack.pop()
            pts.append((cy, cx))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < sh and 0 <= nx < sw and small[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(pts) < 120:
            continue
        ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
        regions.append((len(pts), min(xs) * step, max(xs) * step, min(ys) * step, max(ys) * step))

regions.sort(reverse=True)
print('regions > 120 cells:', len(regions))
for cnt, x0, x1, y0, y1 in regions[:14]:
    print('  area %6d px  x %4d..%4d  y %4d..%4d  (w %4d h %4d)  lum %.0f sat %.2f grad %.1f'
          % (cnt * step * step, x0, x1, y0, y1, x1 - x0, y1 - y0,
             lum[y0:y1, x0:x1].mean(), sat[y0:y1, x0:x1].mean(), mag_s[y0:y1, x0:x1].mean()))
