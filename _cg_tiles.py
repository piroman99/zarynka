import os, sys
from PIL import Image

src = sys.argv[1] if len(sys.argv) > 1 else 'assets/gen/cg_rec23_a__gpt-image-2_0.png'
im = Image.open(src).convert('RGB')
W, H = im.size
print('size', W, H)

out = '_sat'
os.makedirs(out, exist_ok=True)
base = os.path.splitext(os.path.basename(src))[0]

# три плитки: левая (Екатерина), центр (стол), правая (Сергей) + окно сверху
tiles = {
    'L': (0, 0, int(W * 0.42), H),
    'C': (int(W * 0.30), 0, int(W * 0.70), H),
    'R': (int(W * 0.58), 0, W, H),
    'TOP': (int(W * 0.40), 0, W, int(H * 0.45)),
}
for k, box in tiles.items():
    c = im.crop(box)
    # апскейл x2 для читаемости мелких деталей
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    if c.width > 1500:
        c = c.resize((1500, int(c.height * 1500 / c.width)), Image.LANCZOS)
    p = os.path.join(out, '%s_%s.png' % (base, k))
    c.save(p)
    print(p, c.size)
