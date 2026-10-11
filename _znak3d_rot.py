# -*- coding: utf-8 -*-
"""Черновик вращения значка на ЧЕСТНОМ 3D (проверка физики рёбра).
Вращение 0->180° с паузой на ребре (90°). 0 ₽.
Выход: out/znak3d_rot_draft.mp4
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
OUTDIR = os.path.join(HERE, '.tmp_znak3d')
OUT = os.path.join(HERE, 'out', 'znak3d_rot_draft.mp4')
REVIEW = os.path.join(HERE, 'assets', 'review')
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'

# подгрузим рендер призмы из _znak3d.py
_src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
_ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(_src, '_znak3d.py', 'exec'), _ns)
render3d = _ns['render']

W, H, FPS = 1280, 720, 25


def ease(x):
    return x * x * (3 - 2 * x)


def eio(x):
    return 4 * x**3 if x < 0.5 else 1 - (-2 * x + 2)**3 / 2


def angle_at(t):
    """Ребро — МЕЛЬКОМ: без паузы на 90°, сплошной проход (правка заказчика 2026-10-11)."""
    if t < 0.5:
        return 0.0
    if t < 2.30:
        return 180.0 * eio((t - 0.5) / 1.80)
    return 180.0


def make_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2) / (W * 0.62)
    r = np.clip(r, 0, 1)
    out = np.zeros((H, W, 3), np.float32)
    for i, (co, ci) in enumerate(zip((5, 5, 14), (20, 18, 42))):
        out[:, :, i] = co * r + ci * (1 - r)
    return Image.fromarray(out.astype(np.uint8), 'RGB')


BG = make_bg()


def render(t):
    a = angle_at(t)
    zn = render3d(a, w=1280, h=1280)                 # квадрат, обрежем по центру
    zn = zn.crop((0, 280, 1280, 1000)).resize((1280, 720), Image.LANCZOS)
    bg = BG.copy().convert('RGBA')
    zn = zn.convert('RGBA')
    # лёгкое свечение металла в момент ребра
    edge = math.exp(-((a - 90.0) / 22.0) ** 2)
    if edge > 0.05:
        gl = zn.filter(ImageFilter.GaussianBlur(18))
        ga = np.array(gl).astype(np.float32)
        ga[:, :, :3] = np.clip(ga[:, :, :3] * 1.5 + np.array([60, 45, 10]), 0, 255)
        ga[:, :, 3] = np.clip(ga[:, :, 3] * edge, 0, 255)
        bg = Image.alpha_composite(bg, Image.fromarray(ga.astype(np.uint8), 'RGBA'))
    bg = Image.alpha_composite(bg, zn)
    # титул после 4.2 c
    if t > 4.2:
        ta = ease(min(1.0, (t - 4.2) / 0.9))
        d = ImageDraw.Draw(bg)
        f1 = ImageFont.truetype(GOTHIC, 120)
        txt = 'З А Р Я Н К А'
        w1 = d.textlength(txt, font=f1)
        d.text(((W - w1) / 2, 120), txt, font=f1,
               fill=(248, 240, 225, int(255 * ta)))
    return bg.convert('RGB')


if '--frames' in sys.argv:
    for tt in (0.0, 1.4, 2.2, 3.3, 4.8):
        render(tt).save(os.path.join(REVIEW, 'review_49_rot_%.1f.png' % tt))
    print('кадры сохранены')
    sys.exit(0)

os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
NF = int(FPS * 5.4)
for f in range(NF):
    render(f / FPS).save(os.path.join(OUTDIR, 'f%04d.png' % f))
print('кадров', NF)
r = subprocess.run([FF, '-y', '-framerate', str(FPS), '-i', os.path.join(OUTDIR, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', OUT],
                   capture_output=True, text=True)
print('ffmpeg rc', r.returncode, os.path.relpath(OUT, HERE),
      os.path.getsize(OUT) if os.path.exists(OUT) else 0)
if r.returncode:
    print(r.stderr[-1200:])
