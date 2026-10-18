import os
from PIL import Image
im = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB')
for w, q, ext in ((900, None, 'png'), (640, None, 'png')):
    im2 = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    p = 'assets/review/_t_%d.%s' % (w, ext)
    im2.save(p)
    print(p, os.path.getsize(p), im2.size)
