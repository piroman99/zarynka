import os, sys
from PIL import Image

out = '_sat'
os.makedirs(out, exist_ok=True)
for src in sys.argv[1:]:
    im = Image.open(src).convert('RGB')
    W, H = im.size
    base = os.path.splitext(os.path.basename(src))[0]
    # правая верхняя четверть (плакат/стеллаж) и левая верхняя (окно)
    for tag, box in {'poster': (int(W*0.62), 0, W, int(H*0.55)),
                     'window': (0, 0, int(W*0.45), int(H*0.60))}.items():
        c = im.crop(box)
        c = c.resize((c.width*2, c.height*2), Image.LANCZOS)
        if c.width > 1400:
            c = c.resize((1400, int(c.height*1400/c.width)), Image.LANCZOS)
        p = os.path.join(out, '%s_%s.png' % (base, tag))
        c.save(p)
        print(p, c.size)
