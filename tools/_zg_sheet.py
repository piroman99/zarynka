import json, os
from PIL import Image, ImageDraw, ImageFont

OUT = 'assets/refs/zg'
lst = json.load(open(os.path.join(OUT, '_list.json')))
cell_w, cell_h = 620, 420
cols = 4
rows = (len(lst) + cols - 1) // cols
pad = 8
W = cols * (cell_w + pad) + pad
H = rows * (cell_h + 34 + pad) + pad
sheet = Image.new('RGB', (W, H), (24, 24, 28))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
except Exception:
    font = ImageFont.load_default()

for i, fn in enumerate(lst):
    r, c = divmod(i, cols)
    x = pad + c * (cell_w + pad)
    y = pad + r * (cell_h + 34 + pad)
    im = Image.open(fn).convert('RGB')
    im.thumbnail((cell_w, cell_h))
    sheet.paste(im, (x, y))
    d.text((x + 2, y + cell_h + 6), '%d %s' % (i, os.path.basename(fn)[:52]), fill=(235, 235, 235), font=font)

sheet.save('assets/review/review_128_zg_refs.png')
print(sheet.size, os.path.getsize('assets/review/review_128_zg_refs.png'))
