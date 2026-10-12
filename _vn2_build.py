# -*- coding: utf-8 -*-
"""Сборка контента VN-эп1 (vn2/) «Зарянка».

Делает:
  1) кадры пролога: mock base + оверлеи + грейд «тёплый архив»-lite -> vn2/img/prolog/sN.png
  2) фон приёмной + спрайты -> vn2/img/bg, vn2/img/char
  3) иконку/лого -> vn2/img/logo.png, vn2/icons/icon-*.png
  4) vn2/content.js — узлы эп1: титул -> значок(video) -> пролог S1..S7 -> приёмная
Текст — АВТОРСКИЙ ДОСЛОВНО из assets/story.txt (строки 5,7,9 = пролог; 13..67 = приёмная).
"""
import os, json, re, shutil, sys
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(HERE, 'vn2')
IMG = os.path.join(VN2, 'img')
MOCK = os.path.join(HERE, 'assets', 'mock', 'prolog')
GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')
STORY = os.path.join(HERE, 'assets', 'story.txt')

W, H = 1920, 1080

for d in (os.path.join(IMG, 'prolog'), os.path.join(IMG, 'bg'),
          os.path.join(IMG, 'char'), os.path.join(VN2, 'icons')):
    os.makedirs(d, exist_ok=True)

# ---- грейд «тёплый архив»-lite (как в _prolog_animatic.py) --------------
_CM = np.array([[0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]], np.float32)


def grade(im):
    a = np.asarray(im.convert('RGB'), np.float32)
    s = np.clip(a @ _CM.T, 0, 255)
    b = 0.45 * s + 0.55 * a
    b[..., 0] = np.clip(b[..., 0] * 1.035, 0, 255)
    b[..., 1] = np.clip(b[..., 1] * 1.005, 0, 255)
    b[..., 2] = np.clip(b[..., 2] * 0.930, 0, 255)
    b = np.clip((b - 128.0) * 1.07 + 128.0, 0, 255)
    return Image.fromarray(b.astype(np.uint8), 'RGB')


# ---- 1) кадры пролога ---------------------------------------------------
PROLOG_OVL = {
    's1': ['s1_poster'],
    's2': [],
    's3': ['s3_q1', 's3_q2', 's3_q3'],
    's4': ['s4_video', 's4_q'],
    's5': ['s5_posters', 's5_soviet', 's5_seats'],
    's6': [],
    's7': [],
}
for n, ovls in PROLOG_OVL.items():
    base = Image.open(os.path.join(MOCK, n + '_base.png')).convert('RGBA')
    for ov in ovls:
        p = os.path.join(MOCK, ov + '.png')
        if os.path.exists(p):
            base = Image.alpha_composite(base, Image.open(p).convert('RGBA'))
    im = grade(base.convert('RGB')).resize((W, H), Image.LANCZOS)
    im.save(os.path.join(IMG, 'prolog', n + '.png'))
    print('prolog', n, '->', os.path.relpath(os.path.join(IMG, 'prolog', n + '.png'), HERE))

# ---- вырезка фона (плоский фон) для спрайтов ---------------------------
def cutout(im, tol=34):
    """Убрать СВЯЗАННЫЙ с краями фон ПО ЦВЕТОВОЙ ДИСТАНЦИИ от образца фона
    (flood fill). Не зависит от того, белый фон или светло-серый; однотипная
    одежда внутри фигуры не трогается — она не связана с краем."""
    a = np.asarray(im.convert('RGB'), np.float32)
    h, w, _ = a.shape
    # образец фона: верхняя полоса + верхние части левого/правого борта
    ring = np.concatenate([a[:8].reshape(-1, 3),
                           a[:h * 3 // 5, :8].reshape(-1, 3),
                           a[:h * 3 // 5, -8:].reshape(-1, 3)])
    seed = np.median(ring, 0)
    dist = np.sqrt(((a - seed) ** 2).sum(2))
    cand = dist <= tol
    vis = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if cand[y, x] and not vis[y, x]:
                vis[y, x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if cand[y, x] and not vis[y, x]:
                vis[y, x] = True; dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and cand[ny, nx] and not vis[ny, nx]:
                vis[ny, nx] = True; dq.append((ny, nx))
    alpha = np.where(vis, 0, 255).astype(np.uint8)
    A = Image.fromarray(alpha, 'L').filter(ImageFilter.GaussianBlur(1.1))
    out = im.convert('RGBA')
    out.putalpha(A)
    print('   cutout seed=%s tol=%d transparent=%.0f%%' % (seed.astype(int).tolist(), tol, 100 * vis.mean()))
    return out


# ---- 2) фон приёмной + спрайты -----------------------------------------
bg_src = os.path.join(GEN, 'ok_office_clean_0.jpg')   # пустой кабинет (без фигур)
Image.open(bg_src).convert('RGB').resize((W, H), Image.LANCZOS).save(
    os.path.join(IMG, 'bg', 'reception.jpg'))
print('bg reception OK')

for dst, src in (('kate.png', os.path.join(GEN, 'kate_overalls_0.png')),
                 ('sergey.png', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg'))):
    out = cutout(Image.open(src))
    out.save(os.path.join(IMG, 'char', dst))
    print('char', dst, out.size, out.mode)

# ---- 3) лого/иконки -----------------------------------------------------
logo = Image.open(os.path.join(GEN, 'logo_b_0.jpg')).convert('RGB')
side = min(logo.size)
logo = logo.crop(((logo.width - side) // 2, (logo.height - side) // 2,
                  (logo.width + side) // 2, (logo.height + side) // 2))
logo.resize((512, 512), Image.LANCZOS).save(os.path.join(IMG, 'logo.png'))
for sz in (192, 512):
    logo.resize((sz, sz), Image.LANCZOS).save(os.path.join(VN2, 'icons', f'icon-{sz}.png'))
print('logo/icons OK')

# ---- 4) текст -----------------------------------------------------------
lines = open(STORY, encoding='utf-8').read().split('\n')
L = {i + 1: ln.strip() for i, ln in enumerate(lines)}

prolog_par = [L[5], L[7], L[9]]
reception_par = {n: L[n] for n in range(13, 68)
                 if L.get(n) and not L[n].startswith('*')}

# делим длинный 9-й абзац на кадры S3..S7
p9 = L[9]
cut = p9.find('Кто-то на скорую руку')
cut2 = p9.find('Через неделю лозунг')
cut3 = p9.find('Любой мог подать заявку')
cut4 = p9.find('Тысячи людей вспомнили')
SEG9 = [p9[:cut], p9[cut:cut2], p9[cut2:cut3], p9[cut3:cut4], p9[cut4:]]

SENT = re.compile(r'(?<=[.!?…])\s+(?=[А-ЯA-Z«—])')


def pages(text, maxn=2):
    """абзац -> страницы по 1-2 предложения (не «полотно»)."""
    parts = [s.strip() for s in SENT.split(text) if s.strip()]
    out, cur = [], []
    for s in parts:
        cur.append(s)
        if len(cur) >= maxn:
            out.append(' '.join(cur)); cur = []
    if cur:
        out.append(' '.join(cur))
    return out


nodes = []
nodes.append({'t': 'title'})
nodes.append({'t': 'znak', 'video': '../out/znak3d_rot_draft.mp4',
              'caption': 'Зарянка'})

# пролог: кадр + страницы дословного текста + закадр (существующий vo_prolog2)
PROLOG = [('s1', [prolog_par[0]], 's1'),
          ('s2', [prolog_par[1]], 's2'),
          ('s3', [SEG9[0]], 's3'),
          ('s4', [SEG9[1]], 's4'),
          ('s5', [SEG9[2]], 's5'),
          ('s6', [SEG9[3]], 's6'),
          ('s7', [SEG9[4]], None)]
for name, texts, vo in PROLOG:
    pgs = []
    for tx in texts:
        for p in pages(tx):
            pgs.append({'tx': p})
    node = {'t': 'scene', 'id': name, 'bg': f'img/prolog/{name}.png',
            'music': 'prolog', 'pages': pgs}
    if vo:
        node['vo'] = f'audio/{vo}.mp3'      # плейсхолдер (ужатый клип) — см. vn2/README
    nodes.append(node)

# приёмная: фон + спрайты + дословный текст, с говорящими
SPEAK = {15: 'Старик', 23: 'Сергей', 25: 'Екатерина', 29: 'Сергей', 31: 'Екатерина',
         33: 'Сергей', 37: 'Сергей', 41: 'Сергей', 43: 'Екатерина', 45: 'Сергей',
         47: 'Екатерина', 49: 'Сергей', 51: 'Екатерина', 53: 'Сергей', 57: 'Сергей',
         61: 'Сергей', 63: 'Екатерина', 65: 'Сергей', 67: 'Екатерина'}
NAME = {'Сергей': 'Лихнецкий Сергей', 'Екатерина': 'Екатерина Ивановна',
        'Старик': 'Старик'}
SPRITE = {'Сергей': 'img/char/sergey.png', 'Екатерина': 'img/char/kate.png'}

kate_pgs = []
for n in sorted(reception_par):
    who = SPEAK.get(n, '')
    for p in pages(reception_par[n], 2):
        pg = {'tx': p}
        # имя — только для ПРЯМОЙ РЕЧИ (страница начинается с тире); иначе — авторский нарратив
        if who and p.lstrip().startswith('—'):
            pg['who'] = who
            pg['name'] = NAME[who]
        kate_pgs.append(pg)
nodes.append({'t': 'scene', 'id': 'reception', 'bg': 'img/bg/reception.jpg',
              'music': 'reception', 'pages': kate_pgs})

data = {
    'title': 'ЗАРЯНКА',
    'episode': 'Эпизод 1 · «Пролог. Приёмная комиссия»',
    'byline': 'по рассказу Александра «Котобус» Горбова',
    'music': {'prolog': '../assets/audio/sketch/prolog_bed_soft_0.mp3',
              'reception': '../assets/audio/sketch/vn_reception_soft_0.mp3'},
    'nodes': nodes,
}
out = os.path.join(VN2, 'content.js')
with open(out, 'w', encoding='utf-8') as f:
    f.write('// Сгенерировано _vn2_build.py — не править вручную.\n')
    f.write('window.VN = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
tot = sum(len(n.get('pages', [])) for n in nodes)
print('content.js -> %d узлов, %d страниц' % (len(nodes), tot))
for n in nodes:
    print('  ', n['t'], n.get('id', ''), 'стр=%d' % len(n.get('pages', [])))
