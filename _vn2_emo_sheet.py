import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
items = [
    ('kate base',            'assets/gen/kate_overalls_0.png'),
    ('kate smile NEW',       'assets/gen/kate_smile_0.jpg'),
    ('kate sad (exists)',    'assets/gen/kate_sad_0.png'),
    ('sergey base',          'assets/gen/sergey_eng_old__flux-2_0.jpg'),
    ('sergey smile NEW',     'assets/gen/sergey_smile_0.jpg'),
    ('sergey concerned NEW', 'assets/gen/sergey_concerned_0.jpg'),
    ('STARIK NEW',          'assets/gen/starik_0.jpg'),
]
TH = 520
tiles = []
for lab, p in items:
    im = Image.open(os.path.join(HERE, p)).convert('RGB')
    w, h = im.size
    nw = max(1, int(w * TH / h))
    tiles.append((lab, im.resize((nw, TH), Image.LANCZOS)))

pad, capH = 10, 34
W = sum(t.size[0] for _, t in tiles) + pad * (len(tiles) + 1)
sheet = Image.new('RGB', (W, TH + capH + pad), (16, 18, 22))
d = ImageDraw.Draw(sheet)
font = None
for fp in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 19); break
x = pad
for lab, t in tiles:
    sheet.paste(t, (x, capH))
    d.text((x, 8), lab, fill=(245, 215, 110), font=font)
    x += t.size[0] + pad
out = os.path.join(HERE, 'assets', 'review', 'review_77_vn2_emotions.png')
sheet.save(out)
print('WROTE', out, sheet.size)
