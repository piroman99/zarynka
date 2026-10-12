import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for p in [
    'assets/sprites/kate_sad.png',
    'assets/sprites/kate_overalls.png',
    'assets/sprites/sergey.png',
    'assets/gen/kate_sad_0.png',
    'assets/gen/kate_overalls_0.png',
    'assets/gen/sergey_eng_old__flux-2_0.jpg',
    'vn2/img/char/kate.png',
    'vn2/img/char/sergey.png',
]:
    fp = os.path.join(HERE, p)
    if not os.path.exists(fp):
        print('MISSING', p); continue
    im = Image.open(fp)
    a = im.mode
    corner = None
    alpha = None
    if 'A' in im.mode:
        px = im.getpixel((0, 0))
        corner = px
        al = im.getchannel('A')
        alpha = (al.getextrema(), round(sum(al.histogram()[0:8]) / (im.size[0]*im.size[1]), 3))
    print(f'{p:52s} {im.size} {a} corner={corner} alpha={alpha}')
