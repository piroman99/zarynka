# -*- coding: utf-8 -*-
"""Значок-видео, версия 2: резче кадр + титул разведён с медальоном.

Готовит СТИЛЛЫ-кандидаты (1920x1080), чтобы заказчик выбрал раскладку,
и замеряет время рендера. Сам mp4 не пишет.

Правки относительно _znak3d_rot.py:
  * рендер 3D в RGBA (альфа из z-буфера) -> медальон можно ставить куда угодно
    на градиентном фоне, а не «квадратом» с плоским фоном;
  * текстуры граней 256 -> TEXW (источник 1200x1200, больше деталей);
  * суперсэмплинг 2x + LANCZOS (гладкие края);
  * F (фокус) параметр -> размер медальона в кадре;
  * кадр 1920x1080.
"""
import os, sys, math, time, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.join(HERE, 'assets', 'review')
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'

# ---------- грузим геометрию из _znak3d.py с правками ----------
src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
src = src.replace('tex.resize((256, 256), Image.LANCZOS)',
                  'tex.resize((TEXW, TEXW), Image.LANCZOS)')
src = src.replace('uu = np.clip((u * 255).astype(int), 0, 255)',
                  'uu = np.clip((u * (TEXW - 1)).astype(int), 0, TEXW - 1)')
src = src.replace('vv = np.clip((v * 255).astype(int), 0, 255)',
                  'vv = np.clip((v * (TEXW - 1)).astype(int), 0, TEXW - 1)')
src = src.replace("    return Image.fromarray(canvas['img'])",
                  "    a = np.where(canvas['zbuf'] < 1e8, 255, 0).astype(np.uint8)\n"
                  "    return Image.fromarray(np.dstack([canvas['img'], a]), 'RGBA')")
NS = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d', 'TEXW': 1024}
exec(compile(src, '_znak3d.py', 'exec'), NS)
render3d = NS['render']


def medallion(theta_deg, radius, tex=1024, ss=2):
    """Медальон с альфой: диаметр в кадре = 2*radius px, края сглажены."""
    NS['TEXW'] = tex
    side = int(2 * radius * ss) + 120          # запас на пятиугольник
    NS['F'] = radius * NS['CAM_D'] * ss        # радиус в пикселях = F/CAM_D
    im = render3d(theta_deg, w=side, h=side)
    return im.resize((side // ss, side // ss), Image.LANCZOS)


def make_bg(W, H):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2) / (W * 0.62)
    r = np.clip(r, 0, 1)
    out = np.zeros((H, W, 3), np.float32)
    for i, (co, ci) in enumerate(zip((5, 5, 14), (20, 18, 42))):
        out[:, :, i] = co * r + ci * (1 - r)
    return Image.fromarray(out.astype(np.uint8), 'RGB')


def frame(W, H, theta, radius, cy, title_px, title_y, tex=1024, title=True, glow=True,
          title_alpha=1.0):
    bg = make_bg(W, H).convert('RGBA')
    med = medallion(theta, radius, tex=tex)
    # свечение металла в момент ребра (как в принятом черновике)
    k = math.exp(-((theta - 90.0) / 22.0) ** 2)
    if glow and k > 0.05:
        gl = med.filter(ImageFilter.GaussianBlur(max(14.0, radius * 0.07)))
        ga = np.asarray(gl).astype(np.float32)
        ga[..., :3] = np.clip(ga[..., :3] * 1.5 + np.array([60, 45, 10]), 0, 255)
        ga[..., 3] = np.clip(ga[..., 3] * k, 0, 255)
        gl = Image.fromarray(ga.astype(np.uint8), 'RGBA')
        pad = int(radius * 0.6)
        wide = Image.new('RGBA', (gl.width + 2 * pad, gl.height + 2 * pad), (0, 0, 0, 0))
        wide.paste(gl, (pad, pad), gl)
        bg.paste(wide, (int(W / 2 - med.width / 2) - pad, int(cy - med.height / 2) - pad), wide)
    bg.paste(med, (int(W / 2 - med.width / 2), int(cy - med.height / 2)), med)
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(GOTHIC, title_px)
    txt = 'З А Р Я Н К А'
    w1 = d.textlength(txt, font=f1)
    if title and title_alpha > 0.001:
        # титул на отдельном слое: ImageDraw на RGBA не смешивает, а ПЕРЕЗАПИСЫВАЕТ альфу
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text(((W - w1) / 2, title_y), txt, font=f1,
                                 fill=(248, 240, 225, int(255 * max(0.0, min(1.0, title_alpha)))))
        bg = Image.alpha_composite(bg, lay)
    return bg.convert('RGB'), w1




if __name__ == '__main__':
    # ---- замер времени ----
    t0 = time.time(); medallion(180.0, 150, tex=256, ss=1); t_lo = time.time() - t0
    t0 = time.time(); medallion(180.0, 300, tex=1024, ss=2); t_hi = time.time() - t0
    print('рендер: 256/150px %.2f s | 1024/300px+ss2 %.2f s' % (t_lo, t_hi))
    print('на 135 кадров при 25 fps: %.1f мин' % (t_hi * 135 / 60))

    W, H = 1920, 1080
    # кандидаты: (имя, радиус медальона, центр по Y, кегль титула, верх титула)
    # пятиугольник: высота 1.809*R, ширина 1.902*R
    cands = [
        ('A', 290, 430, 170, 800),
        ('B', 320, 440, 150, 830),
        ('C', 290, 560, 170, 100),
    ]
    for name, r, cy, tp, ty in cands:
        for th in (180.0, 90.0, 0.0):
            img, tw = frame(W, H, th, r, cy, tp, ty)
            p = os.path.join(REVIEW, '_zn2_%s_%03d.png' % (name, int(th)))
            img.save(p)
            med_h, med_w = 1.809 * r, 1.902 * r
            print('%s %3d: медальон %.0fx%.0f y %.0f..%.0f | титул %.0f px y %d..%.0f'
                  % (name, int(th), med_w, med_h, cy - med_h / 2, cy + med_h / 2,
                     tw, ty, ty + 1.0 * tp))

    # лист сравнения: было (кадр из старого видео) / A / B / C
    old = os.path.join(REVIEW, '_znchek_4.9.png')
    tiles = []
    if os.path.exists(old):
        tiles.append(('БЫЛО: 1280x720, буквы на жетоне', Image.open(old).convert('RGB')))
    for name, r, cy, tp, ty in cands:
        tiles.append(('ВАРИАНТ %s (жетон %.0f px)' % (name, 1.809 * r),
                      Image.open(os.path.join(REVIEW, '_zn2_%s_180.png' % name)).convert('RGB')))
    tw_, gap = 860, 12
    sheet = Image.new('RGB', (tw_ * len(tiles) + gap * (len(tiles) + 1), int(tw_ * 9 / 16) + 44),
                      (16, 16, 20))
    d = ImageDraw.Draw(sheet)
    for i, (cap, im) in enumerate(tiles):
        x = gap + i * (tw_ + gap)
        sheet.paste(im.resize((tw_, int(tw_ * 9 / 16)), Image.LANCZOS), (x, 34))
        d.text((x, 10), cap, font=ImageFont.truetype(GOTHIC, 18), fill=(255, 210, 130))
    out = os.path.join(REVIEW, 'review_109_znak_title.png')
    sheet.save(out)
    print('лист:', os.path.relpath(out, HERE), sheet.size)
