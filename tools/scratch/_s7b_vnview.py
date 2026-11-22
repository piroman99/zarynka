import os
from PIL import Image
im = Image.open('assets/review/review_96_s7_vn_ok.png').convert('RGB')
print(im.size)
w = 1400
im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(
    'assets/review/review_130b_s7_vn_view.jpg', quality=86)
print(os.path.getsize('assets/review/review_130b_s7_vn_view.jpg'))
