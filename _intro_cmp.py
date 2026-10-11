# -*- coding: utf-8 -*-
"""Сравнительный лист К1 vs К2 — кадры берём из готовых mp4 (ffmpeg)."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
TMP = os.path.join(HERE, '.tmp_cmp')
os.makedirs(TMP, exist_ok=True)

beats = [0.4, 1.3, 2.0, 2.6, 3.2, 3.8, 4.6, 5.4]
tw, th = 470, 264


def frames(mp4, tag):
    out = []
    for t in beats:
        dst = os.path.join(TMP, f'{tag}_{int(t*100):03d}.png')
        subprocess.run([FF, '-y', '-ss', str(t), '-i', mp4, '-frames:v', '1',
                        '-vf', 'scale=%d:%d' % (tw, th), dst], capture_output=True)
        out.append(Image.open(dst).convert('RGB'))
    return out


f1 = frames(os.path.join(HERE, 'out', 'intro_k1_draft.mp4'), 'k1')
f2 = frames(os.path.join(HERE, 'out', 'intro_k2_draft.mp4'), 'k2')

sheet = Image.new('RGB', (8 * tw + 9 * 10, 2 * th + 92), (14, 14, 18))
d = ImageDraw.Draw(sheet)
d.text((20, 14), 'Интро «Зарянка»: К1 (птица улетает) vs К2 (значок-иллюминатор)',
       font=ImageFont.truetype(GOTHIC, 28), fill=(255, 130, 120))
d.text((20, 52), 'верх — К1, низ — К2', font=ImageFont.truetype(LATO, 22), fill=(170, 170, 180))
for i, t in enumerate(beats):
    x = 10 + i * (tw + 10)
    sheet.paste(f1[i], (x, 84))
    sheet.paste(f2[i], (x, 84 + th + 10))
    d.text((x + 6, 88), '%.1f c' % t, font=ImageFont.truetype(LATO, 20), fill=(255, 220, 120))
out = os.path.join(HERE, 'assets', 'review', 'review_33_k1_vs_k2.png')
sheet.save(out)
print(out, sheet.size)
