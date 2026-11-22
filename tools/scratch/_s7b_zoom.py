import os
from PIL import Image, ImageDraw, ImageFont
import _s7_plaque2 as P

im = Image.open('assets/final/prolog/s7.png').convert('RGB')
W, H = im.size
s = W / 2400.0
bx = P.STYLES['a']['box']
x0, y0, x1, y1 = [int(round(v * s)) for v in bx]
pad = 16
c = im.crop((max(0, x0 - pad), max(0, y0 - pad), x1 + pad, y1 + pad))
z = 8
c = c.resize((c.width * z, c.height * z), Image.LANCZOS)
c.save('assets/review/_plaque_zoom8.png')
print('crop', c.size, os.path.getsize('assets/review/_plaque_zoom8.png'))

# рядом — тот же кроп с кадра без таблички (для сравнения «есть/нет»)
import numpy as np
base = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB').resize((2400, 1350), Image.LANCZOS)
# без виньетки не сравнить честно; берём из final, замазав табличку средним тоном стены
none = im.copy()
a = np.asarray(im).astype(np.float32)
wall_rgb = tuple(int(v) for v in a[y0:y1, 2:max(3, x0)].reshape(-1, 3).mean(0))
ImageDraw.Draw(none).rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=wall_rgb)
c2 = none.crop((max(0, x0 - pad), max(0, y0 - pad), x1 + pad, y1 + pad))
c2 = c2.resize((c2.width * z, c2.height * z), Image.LANCZOS)

f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
sheet = Image.new('RGB', (c.width * 2 + 30, c.height + 34), (22, 22, 26))
d = ImageDraw.Draw(sheet)
sheet.paste(c2, (10, 10))
sheet.paste(c, (c.width + 20, 10))
d.text((10, c.height + 14), 'стена без таблички  /  вариант A (8x)', fill=(235, 235, 235), font=f)
sheet.save('assets/review/review_133_s7_plaque_zoom.png')
print(sheet.size, os.path.getsize('assets/review/review_133_s7_plaque_zoom.png'))
