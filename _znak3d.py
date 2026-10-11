# -*- coding: utf-8 -*-
"""3D-модель значка «Зарянка» — ЧЕСТНАЯ ГЕОМЕТРИЯ (софтверный рендер, numpy+PIL, 0 ₽).

Значок = пятиугольная ПРИЗМА:
  - лицо (лого B, птица вправо),  - оборот (иллюминатор: звёзды+Марс),
  - 5 плоских БОКОВЫХ граней (рёбра), на одной — гравировка-пасхалка.
Перспективная проекция, отсечение невидимых граней (выпуклый => корректно),
текстуры через гомографию плоскости. Вращение вокруг вертикальной оси Y.

Проверка геометрии (без сборки видео):  python3 _znak3d.py --sheet
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
REVIEW = os.path.join(HERE, 'assets', 'review')
LOGO = os.path.join(GEN, 'logo_b_0.jpg')
FRONT_TEX = os.path.join(GEN, 'znachek_k1.png')          # лицо (уже нарисовано)
BACK_TEX = os.path.join(GEN, 'znachek_k2_back.png')      # оборот-иллюминатор
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'

RIB_TEXT = 'ЛМД · Ц. 67 КОП.'
R = 1.0                       # радиус описанной окружности пятиугольника
T = 0.10                      # толщина значка (ребро)
CAM_D = 6.0                   # дистанция камеры
F = 1500.0                    # фокус в пикселях (масштаб проекции)
SS = 2                        # суперсэмплинг
OUT_W, OUT_H = 1280, 1280


# ---------- геометрия ----------
def pent_angles():
    """Углы в ТОЙ ЖЕ конвенции, что генератор значка (PIL, y-вниз): -90 + 72k."""
    return [math.radians(-90 + 72 * k) for k in range(5)]


def prism_vertices():
    """10 вершин: [0..4] лицо (z=+T/2), [5..9] оборот (z=-T/2).
    Мировые координаты — y-вверх: (R cos a, -R sin a). Порядок совпадает с текстурой."""
    pts = []
    for a in pent_angles():
        pts.append((R * math.cos(a), -R * math.sin(a), +T / 2))
    for a in pent_angles():
        pts.append((R * math.cos(a), -R * math.sin(a), -T / 2))
    return np.array(pts, float)


def rot_y(theta):
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)


def proj_matrix(cx, cy):
    """3x4: [X,Y,Z,1] -> [sx_h, sy_h, sw]  (камера в (0,0,CAM_D), взгляд -Z)."""
    return np.array([[F, 0, -cx, cx * CAM_D],
                     [0, -F, -cy, cy * CAM_D],
                     [0, 0, -1.0, CAM_D]], float)


# ---------- текстуры ----------
def load_pent_tex(path):
    """Текстура-квадрат, где пятиугольник вписан (совпадает с генератором znachek)."""
    im = Image.open(path).convert('RGB')
    return im


def side_tex(w=48, h=512, text=None):
    """Боковая грань: золотой градиент; если text — вертикальная гравировка."""
    im = Image.new('RGB', (w, h), (150, 116, 52))
    d = ImageDraw.Draw(im)
    for x in range(w):
        prof = math.sin(math.pi * x / max(1, w - 1))
        col = tuple(int(120 + (232 - 120) * prof) if i < 2 else int(40 + (150 - 40) * prof) for i in range(3))
        d.line([(x, 0), (x, h)], fill=col)
    if text:
        f = ImageFont.truetype(LATO_B, max(10, int(w * 0.72)))
        tw = d.textlength(text, font=f)
        tmp = Image.new('RGBA', (int(tw) + 6, w), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.text((3, (w - f.size) // 2), text, font=f, fill=(112, 84, 38))
        tmp = tmp.rotate(90, expand=True)
        im.paste(tmp, (int((w - tmp.width) / 2), int((h - tmp.height) / 2)), tmp)
    return im


# ---------- рендер грани: гомография UV-текстуры -> экран ----------
def _homography(src, dst):
    """H: (u,v)->(x,y) по 4 соответствиям (DLT, 8x8)."""
    A = []
    b = []
    for (u, v), (x, y) in zip(src, dst):
        A.append([u, v, 1, 0, 0, 0, -x * u, -x * v])
        b.append(x)
        A.append([0, 0, 0, u, v, 1, -y * u, -y * v])
        b.append(y)
    A = np.array(A, float)
    b = np.array(b, float)
    h = np.linalg.solve(A, b)
    return np.array([[h[0], h[1], h[2]],
                     [h[3], h[4], h[5]],
                     [h[6], h[7], 1.0]], float)


def render_face(canvas, depth, proj, verts_world, uv, tex, shade, flip_u=False):
    """verts_world:(N,3) точки грани; uv:(N,2) — координаты в текстуре (мэппинг по вершинам)."""
    N = len(verts_world)
    sh = (proj @ np.column_stack([verts_world, np.ones(N)]).T)   # 3xN
    sw = sh[2]
    if np.any(sw <= 1e-6):
        return
    sx = sh[0] / sw
    sy = sh[1] / sw
    # гомография UV(текстуры) -> экран, минимум 4 соответствия
    Hm = _homography(uv[:4], np.column_stack([sx[:4], sy[:4]]))
    try:
        Hi = np.linalg.inv(Hm)
    except np.linalg.LinAlgError:
        return
    x0 = max(0, int(np.floor(sx.min()))); x1 = min(canvas['W'] - 1, int(np.ceil(sx.max())))
    y0 = max(0, int(np.floor(sy.min()))); y1 = min(canvas['H'] - 1, int(np.ceil(sy.max())))
    if x1 < x0 or y1 < y0:
        return
    xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
    # point-in-polygon (ray casting, вект.)
    poly = np.column_stack([sx, sy])
    inside = np.zeros(xs.shape, bool)
    for i in range(N):
        x1p, y1p = poly[i]; x2p, y2p = poly[(i + 1) % N]
        cond = ((y1p > ys) != (y2p > ys))
        xint = (x2p - x1p) * (ys - y1p) / ((y2p - y1p) + 1e-12) + x1p
        inside ^= cond & (xs < xint)
    if not inside.any():
        return
    px = xs[inside]; py = ys[inside]
    hom = np.array([px, py, np.ones_like(px)], float)
    uvw = Hi @ hom
    uw = uvw[2]
    u = uvw[0] / uw; v = uvw[1] / uw
    if flip_u:
        u = 1.0 - u
    tex_np = np.asarray(tex.resize((256, 256), Image.LANCZOS), float)
    uu = np.clip((u * 255).astype(int), 0, 255)
    vv = np.clip((v * 255).astype(int), 0, 255)
    col = np.clip(tex_np[vv, uu] * shade, 0, 255).astype(np.uint8)
    zi = canvas['zbuf'][py, px]
    keep = depth < zi
    canvas['img'][py[keep], px[keep]] = col[keep]
    canvas['zbuf'][py[keep], px[keep]] = depth


def cam_depth(verts_rot):
    """Средняя дистанция до камеры (для z-буфера грани)."""
    return float(np.mean(CAM_D - verts_rot[:, 2]))


def render(theta_deg, rib_face=0, w=OUT_W, h=OUT_H):
    theta = math.radians(theta_deg)
    Ry = rot_y(theta)
    V0 = prism_vertices() @ Ry.T
    cx, cy = w / 2, h / 2
    proj = proj_matrix(cx, cy)
    # UV-координаты вершин — в той же конвенции (v: 0 сверху картинки)
    aR = 0.49
    uvs = []
    for a in pent_angles():
        uvs.append((0.5 + aR * math.cos(a), 0.5 + aR * math.sin(a)))
    uvs = np.array(uvs, float)

    front_tex = load_pent_tex(FRONT_TEX)
    back_tex = load_pent_tex(BACK_TEX)
    rib_texs = [side_tex(48, 512, RIB_TEXT if i == rib_face else None) for i in range(5)]

    canvas = {'img': np.zeros((h, w, 3), np.uint8), 'zbuf': np.full((h, w), 1e9), 'W': w, 'H': h}
    canvas['img'][:] = (6, 8, 18)

    faces = []
    # лицо
    faces.append(('front', V0[0:5], uvs, front_tex, np.array([0, 0, 1.0])))
    # оборот
    faces.append(('back', V0[5:10], uvs, back_tex, np.array([0, 0, -1.0])))
    # боковые
    for i in range(5):
        j = (i + 1) % 5
        quad = np.array([V0[i], V0[j], V0[j + 5], V0[i + 5]])
        # нормаль
        e1 = quad[1] - quad[0]; e2 = quad[3] - quad[0]
        nrm = np.cross(e1, e2); nrm = nrm / (np.linalg.norm(nrm) + 1e-9)
        faces.append(('side', quad, np.array([[0, 0], [0, 1], [1, 1], [1, 0]], float), rib_texs[i], nrm))

    # свет
    L = np.array([-0.4, 0.55, 0.75]); L = L / np.linalg.norm(L)
    cam_pos = np.array([0, 0, CAM_D])
    for kind, verts, uv, tex, nrm in faces:
        center = verts.mean(axis=0)
        view = cam_pos - center
        if np.dot(nrm, view) <= 0:            # невидимая грань
            continue
        shade = 0.55 + 0.45 * max(0.0, float(np.dot(nrm, L)))
        if kind == 'back':
            shade *= 0.9
        d = cam_depth(verts)
        render_face(canvas, d, proj, verts, uv, tex, shade, flip_u=(kind == 'back'))
    return Image.fromarray(canvas['img'])


if '--sheet' in sys.argv:
    angles = [0, 18, 36, 54, 72, 90]
    cw, ch = 420, 420
    sheet = Image.new('RGB', (len(angles) * (cw + 10) + 10, ch + 70), (14, 14, 18))
    d = ImageDraw.Draw(sheet)
    d.text((16, 14), '3D-призма значка: поворот 0..90° (ребро должно появляться само)',
           font=ImageFont.truetype(GOTHIC, 26), fill=(255, 130, 120))
    for i, a in enumerate(angles):
        im = render(a).resize((cw, ch), Image.LANCZOS)
        sheet.paste(im, (10 + i * (cw + 10), 60))
        d.text((16 + i * (cw + 10), 64 + ch), '%d°' % a,
               font=ImageFont.truetype(LATO_B, 24), fill=(255, 220, 120))
    out = os.path.join(REVIEW, 'review_46_znak3d_angles.png')
    sheet.save(out)
    print('saved', os.path.relpath(out, HERE), sheet.size)
