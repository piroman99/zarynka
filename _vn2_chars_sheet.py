import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
items = [
    ('kate_overalls_0 (neutral src)', 'assets/gen/kate_overalls_0.png'),
    ('kate_sad_0 (chair scene)',      'assets/gen/kate_sad_0.png'),
    ('sprites/kate_overalls.png',     'assets/sprites/kate_overalls.png'),
    ('sprites/kate_sad.png',          'assets/sprites/kate_sad.png'),
    ('sergey canon (flux-2)',         'assets/gen/sergey_eng_old__flux-2_0.jpg'),
    ('sprites/sergey.png',            'assets/sprites/sergey.png'),
]
TH = 430
tiles = []
labels = []
for lab, p in items:
    im = Image.open(os.path.join(HERE, p))
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    w, h = im.size
    nh = TH
    nw = int(w * nh / h)
    im = im.resize((nw, nh), Image.LANCZOS)
    # checker bg
    bg = Image.new('RGB', (nw, nh), (60, 66, 74))
    for y in range(0, nh, 24):
        for x in range(0, nw, 24):
            if ((x//24 + y//24) % 2) == 0:
                for yy in range(y, min(y+24, nh)):
                    for xx in range(x, min(x+24, nw)):
                        bg.putpixel((xx, yy), (86, 92, 100))
    bg.paste(im, (0, 0), im)
    tiles.append(bg)
    labels.append(lab)

pad = 12
W = sum(t.size[0] for t in tiles) + pad * (len(tiles) + 1)
H = TH + 70
sheet = Image.new('RGB', (W, H), (18, 20, 24))
x = pad
from PIL import ImageDraw, ImageFont
font = None
for fp in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 17); break
d = ImageDraw.Draw(sheet)
for t, lab in zip(tiles, labels):
    sheet.paste(t, (x, 52))
    d.text((x, 18), lab, fill=(240, 210, 120), font=font)
    x += t.size[0] + pad
out = os.path.join(HERE, 'assets', 'review', 'review_75_vn2_chars_emotions.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
sheet.save(out)
print('WROTE', out, sheet.size)
