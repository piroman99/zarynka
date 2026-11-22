import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import _s7_plaque2 as P

base = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB').resize((2400, 1350), Image.LANCZOS)
none = base
a_img = P.plaque(base, 'a')

pad = 10
W1 = 1000
h1 = round(1350 * W1 / 2400)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 19)
sheet = Image.new('RGB', (2 * W1 + 3 * pad, h1 + 2 * pad + 26), (22, 22, 26))
d = ImageDraw.Draw(sheet)
sheet.paste(none.resize((W1, h1), Image.LANCZOS), (pad, pad))
sheet.paste(a_img.resize((W1, h1), Image.LANCZOS), (pad * 2 + W1, pad))
d.text((pad, h1 + pad + 2), 'без таблички   /   вариант A — как видно в полном кадре',
       fill=(235, 235, 235), font=f)
sheet.save('assets/review/review_131b_s7_quiet_full.jpg', quality=92)
print(sheet.size, os.path.getsize('assets/review/review_131b_s7_quiet_full.jpg'))

# численно: насколько табличка выделяется из стены
an = np.asarray(none).astype(np.float32)
aa = np.asarray(a_img).astype(np.float32)
diff = np.abs(aa - an).mean(2)
ys, xs = np.where(diff > 6)
print('pixels изменены сильнее 6: %d, bbox x %d..%d y %d..%d' % (
    len(xs), xs.min(), xs.max(), ys.min(), ys.max()))
print('max diff %.1f, средняя по bbox %.1f' % (diff.max(), diff[ys.min():ys.max(), xs.min():xs.max()].mean()))
