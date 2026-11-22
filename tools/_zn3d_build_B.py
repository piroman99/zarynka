# -*- coding: utf-8 -*-
"""Сборка значка-видео, ВАРИАНТ B (1920x1080).

Титул разведён с медальоном: жетон 609 px в кадре, под ним подпись 870 px,
зазор 141 px. Рендер тот же, что в _zn3d_hi.py (текстура 1024, сс2, альфа).

Тайминг как в принятом черновике: 0-0.5 с стоит, 0.5-2.3 с поворот 0->180,
дальше пауза, титул проявляется с 4.2 с. Всего 5.4 с, 25 fps.

Выход: out/znak3d_rot.mp4 (ФИНАЛ, вариант B) + стиллы в assets/review
"""
import os, sys, math, subprocess, time
from PIL import Image, ImageDraw, ImageFont

import _zn3d_hi as HZ
from _zn3d_hi import frame, REVIEW

HERE = HZ.HERE
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
TMP = os.path.join(HERE, '.tmp_znakB')
OUT = os.path.join(HERE, 'out', 'znak3d_rot.mp4')
GOTHIC = HZ.GOTHIC

W, H, FPS = 1920, 1080, 25
DUR = 5.4
# ---- параметры варианта B ----
RAD, CY, TPX, TY = 320, 440, 150, 830
TITLE_IN = 4.2          # с какого момента проявляется титул
TITLE_FADE = 0.9


def ease(x):
    return x * x * (3 - 2 * x)


def eio(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def angle_at(t):
    """Ребро МЕЛЬКОМ: без паузы на 90°, сплошной проход (правка заказчика 2026-10-11)."""
    if t < 0.5:
        return 0.0
    if t < 2.30:
        return 180.0 * eio((t - 0.5) / 1.80)
    return 180.0


def title_alpha(t):
    if t <= TITLE_IN:
        return 0.0
    return ease(min(1.0, (t - TITLE_IN) / TITLE_FADE))


def render(t):
    return frame(W, H, angle_at(t), RAD, CY, TPX, TY, title=True,
                 title_alpha=title_alpha(t))[0]


if __name__ == '__main__':
    if '--stills' in sys.argv:
        for tt in (0.0, 1.0, 1.4, 1.9, 2.6, 4.0, 4.6, 5.3):
            p = os.path.join(REVIEW, '_znB_t%.1f.png' % tt)
            render(tt).save(p)
            print('стилл t=%.1f  %s' % (tt, os.path.basename(p)))
        sys.exit(0)

    os.makedirs(TMP, exist_ok=True)
    for f in os.listdir(TMP):
        if f.endswith('.png'):
            os.remove(os.path.join(TMP, f))
    NF = int(round(FPS * DUR))
    t0 = time.time()
    for f in range(NF):
        render(f / FPS).save(os.path.join(TMP, 'f%04d.png' % f))
        if f % 25 == 0:
            print('  кадр %d/%d  %.0f s' % (f, NF, time.time() - t0), flush=True)
    print('рендер %d кадров: %.1f s' % (NF, time.time() - t0))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    r = subprocess.run([FF, '-y', '-framerate', str(FPS), '-i', os.path.join(TMP, 'f%04d.png'),
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT],
                       capture_output=True, text=True)
    print('ffmpeg rc', r.returncode, os.path.relpath(OUT, HERE),
          os.path.getsize(OUT) if os.path.exists(OUT) else 0)
    if r.returncode:
        print(r.stderr[-1500:])
