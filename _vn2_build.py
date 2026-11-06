# -*- coding: utf-8 -*-
"""Сборка контента VN-эп1 (vn2/) «Зарянка».

Делает:
  1) кадры пролога: mock base + оверлеи + грейд «тёплый архив»-lite -> vn2/img/prolog/sN.png
  2) фон приёмной + спрайты -> vn2/img/bg, vn2/img/char
  3) иконку/лого -> vn2/img/logo.png, vn2/icons/icon-*.png
  4) vn2/content.js — узлы эп1: титул -> значок(video) -> пролог S1..S7 -> приёмная
Текст — АВТОРСКИЙ ДОСЛОВНО из assets/story.txt (строки 5,7,9 = пролог; 13..67 = приёмная).
Голос — ПОСТРАНИЧНО: у каждой страницы поле vo = audio/vo/<файл>, закадр пишет _vn2_vo.py.
"""
import os, json, re, shutil, subprocess, sys
import hashlib
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(HERE, 'vn2')
IMG = os.path.join(VN2, 'img')
MOCK = os.path.join(HERE, 'assets', 'mock', 'prolog')
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')   # финальные кадры (_prolog_finals.py)
GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')
STORY = os.path.join(HERE, 'assets', 'story.txt')

W, H = 1920, 1080

# ---- формат раздачи -----------------------------------------------------
# СЛОЙ РАЗДАЧИ — WebP q92 (в 7–9× легче PNG, разница на глаз не видна:
# MAE 1.5–2.3 из 255, см. лист review_100_webp_ab.png).
# НЕ трогаем: оригиналы генерации assets/gen/*.jpg и мастера assets/final/prolog/*.png —
# они остаются без потерь, пересборка идёт всегда от них.
WEBP_Q = 92
CLIENT_EXT = '.webp'


def save_client(im, folder, name, **kw):
    """Сохранить картинку для клиента в WebP и убрать устаревший .png/.jpg рядом."""
    p = os.path.join(folder, name + CLIENT_EXT)
    im.save(p, 'WEBP', quality=WEBP_Q, method=6, **kw)
    for old in (name + '.png', name + '.jpg'):
        q = os.path.join(folder, old)
        if os.path.exists(q):
            os.remove(q)
            print('   удалён устаревший', old)
    return p


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
    's1a': [],         # первая страница кадра s1 (2026-11-04): стена Звёздного городка,
                       # граффити «МАРС — ДЕЛО ОБЩЕЕ» нарисовано моделью — своих букв нет
    'p6': [],          # стр. 1 — кадр С МАРСА (вернулся в сборку 2026-11-04)
    'p6luna': [],      # стр. 2 кадра p6 — ЛУННАЯ база (PAGE_BG), мастер уже финальный
    'p7': [],          # цех сборки: новая ракета недостроена (новая генерация 2026-10-25)
    'p8': [],          # гидролаборатория: межпланетный корабль + спускаемый модуль (2026-10-31)
    's3': ['s3_q1', 's3_q2', 's3_q3'],
    's4': ['s4_video', 's4_q'],
    's5': ['s5_posters', 's5_soviet', 's5_seats'],
    's5a': [],         # кадр 11 (2026-11-01): мастера gpt-image-2 уже финальные
    's6': [],
    's7': [],
}
for n, ovls in PROLOG_OVL.items():
    fin = os.path.join(FIN, n + '.png')
    if os.path.exists(fin):                      # финальный кадр flux-2 (+текст-слой)
        base = Image.open(fin).convert('RGB')
        src = 'final'
    else:                                        # фолбэк: мок base + оверлеи
        b = Image.open(os.path.join(MOCK, n + '_base.png')).convert('RGBA')
        for ov in ovls:
            p = os.path.join(MOCK, ov + '.png')
            if os.path.exists(p):
                b = Image.alpha_composite(b, Image.open(p).convert('RGBA'))
        base = b.convert('RGB')
        src = 'mock'
    im = grade(base).resize((W, H), Image.LANCZOS)
    save_client(im, os.path.join(IMG, 'prolog'), n)
    print('prolog', n, '(%s)' % src, '->', os.path.relpath(os.path.join(IMG, 'prolog', n + CLIENT_EXT), HERE))

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
# Приёмная — акварель (новая манера, решение Ивана 2026-10-19); если нового кадра нет,
# берём прежний «чистый кабинет», чтобы сборка не падала.
bg_new = os.path.join(HERE, 'assets', 'pilot', 'pilot_reception_0.png')
bg_src = bg_new if os.path.exists(bg_new) else os.path.join(GEN, 'ok_office_clean_0.jpg')
save_client(Image.open(bg_src).convert('RGB').resize((W, H), Image.LANCZOS),
            os.path.join(IMG, 'bg'), 'reception')
print('bg reception OK')

# кабинет Старика (флешбэк в начале приёмной): акварель, пустая комната,
# спрайт Старика движок кладёт сверху
cab_src = os.path.join(HERE, 'assets', 'pilot', 'pilot_cabinet_0.png')
if os.path.exists(cab_src):
    save_client(Image.open(cab_src).convert('RGB').resize((W, H), Image.LANCZOS),
                os.path.join(IMG, 'bg'), 'cabinet')
    print('bg cabinet OK')
else:
    print('bg cabinet SKIP (нет', cab_src, ')')

# Аллея у ворот (сцена после приёмной, story.txt строки 71..121): ДВА кадра —
#   steps — «вышла из дверей… спустилась по широким ступеням»
#   alley — «на скамейке между зелёных еловых лап сидел юноша» (вариант B, ворота видны)
# Иван 2026-11-04: «надо следующую сцену делать… но сначала фон».
ALLEY_BG = {'steps': 'steps_a', 'alley': 'alley_b'}
for _name, _stem in ALLEY_BG.items():
    _src = None
    for _ext in ('.png', '.jpg'):
        _p = os.path.join(GEN, _stem + '_0' + _ext)
        if os.path.exists(_p):
            _src = _p
    if not _src:
        raise SystemExit('нет кадра сцены «аллея»: %s' % _stem)
    save_client(Image.open(_src).convert('RGB').resize((W, H), Image.LANCZOS),
                os.path.join(IMG, 'bg'), _name)
    print('bg %s OK <- %s' % (_name, _stem))

# базовые спрайты + готовые эмоции (отсутствующие файлы пропускаем;
# остальные эмоции рисует _vn2_emo.py — движок подхватит их без правок)
def first_existing(*cands):
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[0]


CHAR_SRC = {
    'kate.png':     os.path.join(GEN, 'kate_overalls_0.png'),
    'sergey.png':   os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg'),
    'kate_sad.png': os.path.join(GEN, 'kate_sad_0.png'),
    'kate_smile.png': first_existing(os.path.join(GEN, 'kate_smile_0.png'),
                                     os.path.join(GEN, '_kate_v2', 'kate_smile__gpt-image-2_0.png')),
    'sergey_smile.png':     first_existing(os.path.join(GEN, 'sergey_smile_0.png'),
                                           os.path.join(GEN, 'sergey_smile_0.jpg')),
    'sergey_concerned.png': first_existing(os.path.join(GEN, 'sergey_concerned_0.png'),
                                           os.path.join(GEN, 'sergey_concerned_0.jpg')),
    'starik_stern.png': os.path.join(SPR, 'starik_stern.png'),
    # Поэт Лёша Савушкин (2026-11-04): два вида по канону 2016 — с длинной плохой
    # причёской и стриженный. Файлы уже нормированы по плечам (`_poet_norm.py`),
    # лежат RGB на светло-сером фоне — вырезает их тот же cutout(), что и каст.
    'poet.png':              os.path.join(SPR, 'poet_ha_neutral.png'),
    'poet_interested.png':   os.path.join(SPR, 'poet_ha_interested.png'),
    'poet_upset.png':        os.path.join(SPR, 'poet_ha_upset.png'),
    # сидящий поэт на скамейке (сцена «аллея») — правка Ивана 2026-11-05: скамейка больше
    # НЕ часть спрайта (она статичный проп `img/prop/bench`), в кадре — фигура целиком
    # от макушки до ступней; 6 эмоций.
    'poet_seat.png':          os.path.join(SPR, 'poet_seat_neutral.png'),
    'poet_seat_interested.png': os.path.join(SPR, 'poet_seat_interested.png'),
    'poet_seat_upset.png':    os.path.join(SPR, 'poet_seat_upset.png'),
    'poet_seat_shy.png':      os.path.join(SPR, 'poet_seat_shy.png'),
    'poet_seat_sullen.png':   os.path.join(SPR, 'poet_seat_sullen.png'),
    'poet_seat_smile.png':    os.path.join(SPR, 'poet_seat_smile.png'),
    'poet_sh.png':           os.path.join(SPR, 'poet_sh_neutral.png'),
    'poet_sh_tired.png':     os.path.join(SPR, 'poet_sh_tired.png'),
    'poet_sh_inspired.png':  os.path.join(SPR, 'poet_sh_inspired.png'),
}
for dst, src in CHAR_SRC.items():
    if not os.path.exists(src):
        print('char SKIP (нет источника):', dst)
        continue
    _im = Image.open(src)
    # Спрайт уже вырезан с мягкой альфой (поэт, `_poet_matte.py`) — повторный cutout()
    # съел бы тёмные волосы и снова оставил серые пятна в петлях. Такие файлы берём как есть.
    _pre_matted = (_im.mode == 'RGBA' and
                   float((np.asarray(_im.split()[-1]) < 8).mean()) > 0.02)
    out = _im if _pre_matted else cutout(_im)
    # без потерь: на тёмных волосах lossy-webp даёт серую кайму (замер `_poet_hair_check.py`)
    save_client(out, os.path.join(IMG, 'char'), dst.rsplit('.', 1)[0],
                lossless=True if _pre_matted else False)
    print('char', dst, out.size, out.mode, '(pre-matted)' if _pre_matted else '')


# доступные спрайты и эмоции (по фактическим файлам в img/char) — движок
# рисует только то, что есть, и подхватит новые эмоции без правок кода
# Предметы сцены (статичный проп). Скамейка сцены «аллея»: отдельным кадром от спрайта
# (правка Ивана 2026-11-05 №1 и №2: «скамейка должна быть длинной» + «не должна дрожать
# вместе со спрайтом поэта»). Спрайт поэта — без мебели.
PROP_SRC = {'bench': os.path.join(SPR, 'prop_bench.png')}
PROP_DIR = os.path.join(IMG, 'prop')
os.makedirs(PROP_DIR, exist_ok=True)
for _n, _p in PROP_SRC.items():
    if not os.path.exists(_p):
        print('prop SKIP (нет источника):', _n)
        continue
    _im = Image.open(_p).convert('RGBA')
    if _im.height > 700:
        _im = _im.resize((round(_im.width * 700 / _im.height), 700), Image.LANCZOS)
    _im.save(os.path.join(PROP_DIR, _n + '.webp'), 'WEBP', quality=82, method=6)
    print('prop', _n, _im.size)


def char_manifest():
    key_of = {'Сергей': 'sergey', 'Екатерина': 'kate', 'Старик': 'starik',
              'Поэт': 'poet', 'Поэт (стриж.)': 'poet_sh', 'Поэт (на скамейке)': 'poet_seat'}
    # «сидят» — те, у кого в движке особое дыхание (масштаб от нижней кромки, без подскока)
    seated = {'Поэт (на скамейке)'}
    known = ['neutral', 'smile', 'sad', 'concerned', 'stern',
             'interested', 'upset', 'tired', 'inspired', 'shy', 'sullen']
    have = set(os.listdir(os.path.join(IMG, 'char')))
    d = {}
    for who, k in key_of.items():
        emos = {}
        for em in known:
            fn = k + ('' if em == 'neutral' else '_' + em) + CLIENT_EXT
            if fn in have:
                emos[em] = 'img/char/' + fn
        if emos:
            d[who] = {'base': emos.get('neutral') or next(iter(emos.values())),
                      'emos': emos}
            if who in seated:
                d[who]['seated'] = True
    return d


CHARS_AVAIL = char_manifest()

# ---- 3) лого/иконки -----------------------------------------------------
# Лого = КРУГ, а не квадрат: у исходника (logo_b_0.jpg) диск на белом фоне, и на
# тёмном кадре перехода этот белый квадрат светился углами (Иван 2026-10-21:
# «лого в квадрате, а мы договаривались либо в круге, либо в пятиугольнике»).
# Теперь: обрезаем по диску и маскируем всё вне круга в прозрачность (с мягким краем),
# чтобы лого читалось круглым на любом фоне. Иконки для PWA/иконки «на Домой»
# остаются НЕпрозрачными квадратами (iOS/Android сами скругляют).
def _circle_logo(im, size, feather=1.2):
    a = np.asarray(im.convert('RGB'), dtype=np.int16)
    # диск = не-белые пиксели (белый фон генератора); порог с запасом на полутон
    mask = (a.max(axis=2) < 245) | (a.min(axis=2) < 235)
    ys, xs = np.nonzero(mask)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = max(x1 - x0, y1 - y0) / 2.0 + 2          # чуть воздуха по краю
    box = (int(cx - r), int(cy - r), int(cx + r), int(cy + r))
    disc = im.convert('RGB').crop(box).resize((size, size), Image.LANCZOS)
    out = disc.convert('RGBA')
    yy, xx = np.mgrid[0:size, 0:size]
    d = np.hypot(xx - (size - 1) / 2.0, yy - (size - 1) / 2.0)
    rr = size / 2.0 - 1
    alpha = np.clip((rr - d) / feather + 0.5, 0, 1) * 255
    al = np.asarray(out).copy()
    al[:, :, 3] = alpha.astype(np.uint8)
    return Image.fromarray(al, 'RGBA'), disc


logo_src = Image.open(os.path.join(GEN, 'logo_b_0.jpg'))
logo_round, logo_sq = _circle_logo(logo_src, 512)
logo_round.save(os.path.join(IMG, 'logo.png'))          # прозрачный круг (титул)
for sz in (192, 512):
    logo_sq.resize((sz, sz), Image.LANCZOS).save(os.path.join(VN2, 'icons', f'icon-{sz}.png'))

# Значок для перехода между сценами — отдельный файл, чтобы форма выбиралась ОДНОЙ
# строкой и не трогала титул:  TRANS_EMBLEM=circle python3 _vn2_build.py
#   penta  — золотой пятиугольник-жетон из пролога (ВЫБРАН Иваном 2026-10-21, дефолт)
#   circle — диск, как на титуле (прежний вариант)
TRANS_EMBLEM = os.environ.get('TRANS_EMBLEM', 'penta').strip().lower()
if TRANS_EMBLEM == 'penta':
    emb = Image.open(os.path.join(GEN, 'znachek_k1.png')).convert('RGBA')
    emb = emb.crop(emb.split()[3].getbbox())          # обрезать по непрозрачному
    side = max(emb.size)
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(emb, ((side - emb.width) // 2, (side - emb.height) // 2), emb)
    sq.resize((512, 512), Image.LANCZOS).save(os.path.join(IMG, 'trans_logo.png'))
else:
    logo_round.save(os.path.join(IMG, 'trans_logo.png'))
print('logo/icons OK (лого — круг с прозрачным фоном, переход: %s)' % TRANS_EMBLEM)

# Версия значка перехода = хеш самого файла: меняется форма (круг ↔ пятиугольник)
# — меняется адрес, и браузер/Pages не отдаёт старую картинку из кеша.
EMBLEM_VER = hashlib.md5(open(os.path.join(IMG, 'trans_logo.png'), 'rb').read()).hexdigest()[:8]
print('  trans_logo.png v=%s' % EMBLEM_VER)

# ---- 4) текст -----------------------------------------------------------
lines = open(STORY, encoding='utf-8').read().split('\n')
L = {i + 1: ln.strip() for i, ln in enumerate(lines)}

prolog_par = [L[5], L[7], L[9]]
# Кадр s1 — ДВЕ страницы и ДВА кадра (решение Ивана 2026-11-04, развилка A):
#  стр. 1 — «Кто бросил клич…» на стене Звёздного городка с граффити (кадр s1a),
#  стр. 2 — «…поймать этого умника в темной подворотне» на старом кадре s1.
# Смена кадров внутри узла — бесплатный кроссфейд .bg 0.6 с (setBg в app.js).
_cut1 = prolog_par[0].find('Очень уж хотелось')
if _cut1 < 0:
    raise SystemExit('не нашёл границу текста для кадра s1 (стена/подворотня) в L[5]')
s1a_par = prolog_par[0][:_cut1].strip()      # стена, граффити
s1b_par = prolog_par[0][_cut1:].strip()      # тёмная подворотня
# Кадр 6 — хроника первого полёта: кадры С МАРСА (Иван 2026-10-25: «Там скорее кадры
# с Марса нужны», выбран вариант B). Абзац L[7] делится по смыслу: «Один раз были?
# Ну и хорошо…» идёт под архивную хронику, «Но экспедиция потихоньку набиралась…» — под цех S2.
_cut7 = prolog_par[1].find('Но экспедиция потихоньку набиралась')
if _cut7 < 0:
    raise SystemExit('не нашёл границу текста для кадра p6 в L[7]')
# Кадр 7 — цех сборки (Иван 2026-10-25: «вставляем цех из новой генерации»): недостроенная
# ракета = «модули корабля строились». Остаток абзаца («Космонавты начали тренировки…»)
# остаётся у s2.
_s2_all = prolog_par[1][_cut7:].strip()
_cut7b = _s2_all.find('Космонавты начали тренировки')
if _cut7b < 0:
    raise SystemExit('не нашёл границу текста для кадра p7 в L[7]')
p6_par = prolog_par[1][:_cut7].strip()
p7_par = _s2_all[:_cut7b].strip()
p8_par = _s2_all[_cut7b:].strip()   # «Космонавты начали тренировки…» — гидролаборатория
reception_par = {n: L[n] for n in range(13, 68)
                 if L.get(n) and not L[n].startswith('*')}

# делим длинный 9-й абзац на кадры S3..S7
p9 = L[9]
cut = p9.find('Кто-то на скорую руку')
cut2 = p9.find('Через неделю лозунг')
cut3 = p9.find('Любой мог подать заявку')
cut4 = p9.find('Тысячи людей вспомнили')
SEG9 = [p9[:cut], p9[cut:cut2], p9[cut2:cut3], p9[cut3:cut4], p9[cut4:]]

# 2026-11-01 (бриф 9-12): третий кусок делится НА ДВА КАДРА по фразе «Волна требований…»
#   s5a — «лозунг облетел страну» (площадь, плакаты; новый кадр 2026-11-01)
#   s5b — «докатилась до Верховного Совета» (старый «ТРИУМФ», 0 ₽)
_c5 = SEG9[2].find('Волна требований докатилась')
if _c5 < 0:
    raise SystemExit('не нашёл границу текста для кадра 12 (s5b)')
s5a_par = SEG9[2][:_c5].strip()
s5b_par = SEG9[2][_c5:].strip()

SENT = re.compile(r'(?<=[.!?…])\s+(?=[А-ЯA-Z«—])')
STUB = 15          # реплика короче — «обрывок»: склеивается с авторской вставкой
# Разбор абзаца на сегменты и страницы — в общем модуле _text_seg.py:
# тем же кодом пользуется подстрочник _story_cast.py (без запуска сборки).
from _text_seg import segments, pages_of   # noqa: E402
# Версия озвучки: попадает в адрес mp3 (?v=N). Поднимать при любой переозвучке.
# Без неё браузер и GitHub Pages отдают старый файл из кеша (предзагрузка идёт с
# force-cache) — так Иван слышал уже переозвученную страницу старым голосом.
VO_VER = 7


def pages(text, maxn=2):
    """абзац -> страницы по 1-2 предложения (не «полотно»). Без разбора на голоса."""
    parts = [s.strip() for s in SENT.split(text) if s.strip()]
    out, cur = [], []
    for s in parts:
        cur.append(s)
        if len(cur) >= maxn:
            out.append(' '.join(cur)); cur = []
    if cur:
        out.append(' '.join(cur))
    return out


CG_DIR = os.path.join(IMG, 'cg')
os.makedirs(CG_DIR, exist_ok=True)
# имя в vn2 <- исходник в assets/gen (выбор варианта — константы ниже)
CG_P4 = 'cg_p4v3_a'          # P4 на стр. 35..37. v3 = Сергей со спрайта (щетина, жилет, бейдж);
                             # 'a' (общий от окна — принят Иваном 2026-10-25) | 'b' (через плечо).
                             # v2 (бритый, в галстуке) забракован — оставлен исходником в assets/gen.
CG_MUZA = 'cg_muza2'         # «— Муза, — юноша покраснел и отвернулся» (сцена «аллея»).
                             # v1 забракован Иваном 2026-11-05: «скамейка углом к дороге,
                             # так не бывает» → v2: скамейка стоит ВДОЛЬ аллеи.
CG_SAD = 'cg_room_a'         # сникшая Екатерина на стр. 59..61 (принят 2026-10-24)
CG_SOURCES = {'rec_35': CG_P4, 'rec_48': CG_SAD, 'al_muza': CG_MUZA}
# имя файла генерации: у новых партий gpt-image-2 без суффикса модели
CG_FILE = {'rec_35': None, 'rec_48': None, 'al_muza': 'cg_muza2_0.png'}
for _out, _stem in CG_SOURCES.items():
    _src = os.path.join(GEN, CG_FILE.get(_out) or (_stem + '__gpt-image-2_0.png'))
    if not os.path.exists(_src):
        raise SystemExit('нет исходника CG: %s' % _src)
    _cg = Image.open(_src).convert('RGB')
    if _cg.size != (W, H):
        _cg = _cg.resize((W, H), Image.LANCZOS)
    save_client(_cg, CG_DIR, _out)
    print('CG %s OK %dx%d <- %s' % (_out, _cg.width, _cg.height, _stem))

nodes = []
nodes.append({'t': 'title'})
nodes.append({'t': 'znak', 'video': '../out/znak3d_rot.mp4',
              'caption': 'Зарянка'})
# Посвящение — дословно из рассказа (строки 1 и 3); показывается после лого-значка,
# перед первой сценой пролога (Иван 2026-10-24: «мы забыли посвящение»).
nodes.append({'t': 'ded', 'l1': L[1], 'l2': L[3]})

# пролог: кадр + страницы дословного текста + закадр (существующий vo_prolog2)
# камера «двухбит одним кадром» — плавный наезд без склейки (S4 → Марс на панели)
PROLOG_CAM = {'s4': {'from': 1.0, 'to': 1.5, 'x': 0.44, 'y': 0.30, 'hold': 0.9, 'dur': 3.4}}
PROLOG = [('s1', [s1a_par, s1b_par], 's1'),
          ('p6', [p6_par], None),      # хроника первого полёта (Марс); закадр пока не писан
          ('p7', [p7_par], 'p7'),      # цех сборки: модули корабля строились
          ('p8', [p8_par], 'p8'),      # гидролаборатория: тренировки на макете корабля
          ('s3', [SEG9[0]], 's3'),
          ('s4', [SEG9[1]], 's4'),
          ('s5a', [s5a_par], 's5a'),   # лозунг облетел страну — площадь, плакатные тумбы
          ('s5b', [s5b_par], 's5b', 's5'),   # 4-й элемент = ФАЙЛ кадра: тот же «ТРИУМФ» (s5)
          ('s6', [SEG9[3]], 's6'),
          ('s7', [SEG9[4]], None)]

# Кадры ОТДЕЛЬНЫХ СТРАНИЦ внутри узла: (узел, номер страницы) -> файл кадра в
# assets/final/prolog (без расширения). Смена — кроссфейдом .bg 0.6 с.
PAGE_BG = {('s1', 0): 'img/prolog/s1a',   # s1: стр. 1 — стена с граффити, стр. 2 — подворотня
           ('p6', 1): 'img/prolog/p6luna'}  # p6: стр. 1 — кадр С МАРСА, стр. 2 — лунная база

# ---- ТИТР-СЛОЙ КАДРОВ (pg.ovl) ------------------------------------------
# До 2026-11-01 надписи вжигались в PNG (_prolog_finals.py) и висели весь кадр.
# Теперь они живут в движке и появляются ПО СТРАНИЦАМ: страница = фраза.
# Координаты и кегли — в пространстве 2400x1350 (ровно как было в _prolog_finals.py).
def ovl_t(t, size, color, x, y, kind='g', anchor='ma', at=None):
    # at = ФРАЗА строки: подстрока текста страницы, на которой строка появляется
    # (в content.js уезжает долей 0..1). None → строка стоит с начала страницы.
    return {'t': t, 'f': kind, 's': size, 'c': color, 'x': x, 'y': y, 'a': anchor, 'at': at}


def ovl_b(box, color=(6, 8, 14), alpha=150, blur=20):
    return {'b': list(box), 'c': list(color), 'a': alpha, 'bl': blur}


def _norm(s):
    return s.lower().replace('ё', 'е')


def ovl_at(tx, marker):
    """Доля текста страницы, где начинается фраза-маркер (регистр/ё не важны)."""
    i = _norm(tx).find(_norm(marker))
    if i < 0:
        raise SystemExit('титр: маркер %r не найден в тексте %r' % (marker, tx[:60]))
    return round(i / float(max(1, len(tx))), 4)


_FF = os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                   'ffmpeg-linux-x86_64-v7.0.2')
_DUR = {}


def vo_dur(rel):
    """Длительность озвучки страницы, сек (из mp3 через ffmpeg). Кеш на сборку."""
    if rel in _DUR:
        return _DUR[rel]
    p = os.path.join(VN2, rel)
    sec = 0.0
    if os.path.exists(p) and os.path.exists(_FF):
        r = subprocess.run([_FF, '-hide_banner', '-i', p], capture_output=True, text=True)
        m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r.stderr)
        if m:
            sec = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    _DUR[rel] = round(sec, 2)
    return _DUR[rel]


CREAM = '#f6eede'
GREEN = '#7ed680'
GOLD = '#ffd278'
WARM = '#fce2aa'

# ключ = (id узла, номер страницы)
OVL_PAGES = {
    # кадр 9 — зал: подстрочник — один абзац, но надписи идут ПО ФРАЗАМ (at = маркер):
    # «Марс — дело общее?» → хор «Общее!» → «а что же обычных людей нет?»
    ('s3', 0): [ovl_b((620, 330, 1780, 1010), alpha=150, blur=26),
                ovl_t('«МАРС —', 108, CREAM, 1200, 430, at='Марс — дело общее'),
                ovl_t('ДЕЛО ОБЩЕЕ?»', 108, CREAM, 1200, 560, at='Марс — дело общее'),
                ovl_t('«ОБЩЕЕ!»', 86, GREEN, 1200, 720, at='«Общее!»'),
                ovl_t('а что же обычных людей нет?', 52, CREAM, 1200, 860, 'l',
                      at='обычных людей')],
    # кадр 10 — ролик: подпись на экране панели (кегль 61 — 94% ширины экрана ТВ).
    # Появляется на «неудобным вопросом» — подпись и есть этот вопрос.
    ('s4', 0): [ovl_b((738, 684, 1644, 777), color=(4, 5, 10), alpha=180, blur=14),
                ovl_t('а что же обычных людей нет?', 61, CREAM, 1191, 730, 'l', 'mm',
                      at='неудобным вопросом')],
    # кадр 11 — площадь (вариант B кадра, 2026-11-03): полоса лозунга занимает ВСЮ светлую
    # панель-витрину справа (вариант i, выбран Иваном). Панель замерена детектом плоских
    # светлых областей (_s5ab_panels.py): 1119,499,1848,895. Край резкий (blur=0) — это плакат.
    # Кегли подобраны под ширину панели 729 при 92%: 62 / 58 (_s5a_band_B.py).
    ('s5a', 0): [ovl_b((1119, 505, 1848, 890), color=(168, 40, 34), alpha=232, blur=0),
                 ovl_t('МАРС — ДЕЛО ОБЩЕЕ!', 62, CREAM, 1483, 636, at='Марс дело общее'),
                 ovl_t('ДАЁШЬ МАРС ДЛЯ ВСЕХ!', 58, WARM, 1483, 782, at='Даешь Марс')],
    # вторая страница кадра 11 — лозунг уже облетел страну, плакат стоит целиком
    ('s5a', 1): [ovl_b((1119, 505, 1848, 890), color=(168, 40, 34), alpha=232, blur=0),
                 ovl_t('МАРС — ДЕЛО ОБЩЕЕ!', 62, CREAM, 1483, 636),
                 ovl_t('ДАЁШЬ МАРС ДЛЯ ВСЕХ!', 58, WARM, 1483, 782)],
    # кадр 12 — Верховный Совет: чип по центру кадра (вариант A, правка Ивана 2026-11-04):
    # раньше центр был x=960 при центре кадра 1200 → чип висел левее на 240 px.
    # Чип — про «два места для людей с улицы», на этой фразе и появляется.
    ('s5b', 0): [ovl_b((801, 690, 1599, 780), alpha=150, blur=14),
                 ovl_t('ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ', 46, GOLD, 1200, 735, 'g', 'mm',
                       at='два места')],
}
for item in PROLOG:
    name, texts, vo = item[0], item[1], item[2]
    img = item[3] if len(item) > 3 else name
    pgs = []
    for tx in texts:
        for p in pages(tx):
            pgs.append({'tx': p, 'vo': f'audio/vo/{name}_{len(pgs):02d}.mp3'})
    for pg in pgs:
        if name in PROLOG_CAM:
            pg['cam'] = PROLOG_CAM[name]
    for i, pg in enumerate(pgs):
        ov = OVL_PAGES.get((name, i))
        if ov:
            for it in ov:
                if 't' not in it:
                    continue
                if isinstance(it.get('at'), str):
                    it['at'] = ovl_at(pg['tx'], it['at'])     # фраза → доля текста
                elif it.get('at') is None:
                    it['at'] = 0.0
            pg['ovl'] = ov
            pg['vod'] = vo_dur(pg['vo'])          # длительность озвучки — часы титр-слоя
            print('титр %s[%d]: озвучка %.2f с, at=%s'
                  % (name, i, pg['vod'], [it.get('at') for it in ov if 't' in it]))
    node = {'t': 'scene', 'id': name, 'bg': f'img/prolog/{img}{CLIENT_EXT}',
            'music': 'prolog', 'pages': pgs}
    # страница со СВОИМ кадром внутри узла (кроссфейд .bg при входе на страницу)
    for _pi, _bg in PAGE_BG.items():
        if _pi[0] == name:
            dup = {'bg': _bg + CLIENT_EXT}
            pgs[_pi[1]].update(dup)
            print('кадр страницы %s[%d] -> %s' % (name, _pi[1], _bg))
    nodes.append(node)

# приёмная: фон + спрайты + дословный текст, с говорящими
SPEAK = {15: 'Старик', 23: 'Сергей', 25: 'Екатерина', 29: 'Сергей', 31: 'Екатерина',
         33: 'Сергей', 37: 'Сергей', 41: 'Сергей', 43: 'Екатерина', 45: 'Сергей',
         47: 'Екатерина', 49: 'Сергей', 51: 'Екатерина', 53: 'Сергей', 57: 'Сергей',
         61: 'Сергей', 63: 'Екатерина', 65: 'Сергей', 67: 'Екатерина'}
NAME = {'Сергей': 'Лихнецкий Сергей', 'Екатерина': 'Екатерина Ивановна',
        'Старик': 'Старик',
        # поэт по имени представится только после тренировки («Я Лёша, Лёша Савушкин»),
        # поэтому в плашке до того момента — без фамилии
        'Поэт': 'Поэт', 'Поэт (сидя)': 'Поэт'}

# --- приёмная: страницы, каст (кто и где стоит) и эмоции ---
# Эмоции/появления проставлены РУЧНО по смыслу текста (в тексте эмоций нет).
# Привязка — К ТЕКСТУ, а не к номеру страницы: разбивка на страницы меняется
# (с 2026-10-19 реплики и авторский текст разведены), а якоря остаются.
# Якорь — фрагмент начала страницы; эмоция действует до следующей смены.
EMO_ANCHOR = [
    ('Лихнецкому не повезло', 'Старик', 'stern'),
    # Сергей: заученная улыбка на приветствии → озабоченность с «закрыл папку»
    # → тёплая улыбка, когда предлагает вакансии
    ('Добрый день. Добро пожаловать', 'Сергей', 'smile'),
    ('Что она делает здесь?', 'Сергей', 'neutral'),
    ('Сергей с сожалением закрыл папку', 'Сергей', 'concerned'),
    ('Если вы так интересуетесь космосом', 'Сергей', 'smile'),
    # Екатерина: приветливая → нейтрально-недоумённая → поникшая → тёплая улыбка
    ('Здравствуйте, Сергей, вот, пожалуйста', 'Екатерина', 'smile'),
    ('Женщина удивленно смотрела на него', 'Екатерина', 'neutral'),
    ('Вы хотите сказать, что я слишком старая', 'Екатерина', 'sad'),
    ('она внезапно тепло улыбнулась', 'Екатерина', 'smile'),
]
# смена состава: якорь -> сторона ('l' левый / 'r' правый) : (кто, эмоция)
# кто = '-' — УБРАТЬ спрайт с этой стороны (уход персонажа из кадра)
# Флешбэк в кабинете Старика (Сергей попался под горячую руку) → приёмная: Сергей один,
# потом входит Екатерина.
CAST_ANCHOR = [
    ('Лихнецкому не повезло', 'l', 'Старик', 'stern'),
    ('Так и пришлось долгих два месяца', 'l', 'Сергей', 'neutral'),
    # Поэт Лёша Савушкин — его Лихнецкий заворачивает первым делом («длинноволосый поэт…
    # Его он тоже отправил вслед за остальными»). Правка Ивана 2026-11-04: «надо его спрайты
    # сделать, и потом вернуть этот спрайт в отказ лихнецкого в самом начале».
    ('Сегодня первыми кандидатами', 'r', 'Поэт', 'neutral'),
    ('Его он тоже отправил вслед за остальными', 'r', '-', ''),
    # Появление Екатерины — на ОПИСАНИИ (правка Ивана 2026-11-04: «появление Екатерины надо
    # перенести на „Кудрявые седые как снег волосы, мягкое лицо“»). Было: спрайт въезжал
    # только на приветствии «Добрый день. Добро пожаловать в Звездный городок».
    ('Кудрявые седые, как снег, волосы', 'r', 'Екатерина', 'neutral'),
]

# 1) текст + говорящие: реплика и авторский текст разведены по СЕГМЕНТАМ
# (старый баг: голос ставился на весь абзац, и авторский текст между фразами
#  Екатерины читался её же голосом)
raw = []
for n in sorted(reception_par):
    who = SPEAK.get(n, '')
    for kind, p in pages_of(segments(reception_par[n]), 2):
        if kind == 'mix':
            # склеенная страница: реплика + авторская вставка, у каждого сегмента свой голос
            idx = len(raw)
            vos, parts, vwho = [], [], []
            for j, (k, t) in enumerate(p):
                t = re.sub(r'(?<=[а-яё])\.(?=[А-ЯЁ])', '. ', t)
                vos.append('audio/vo/rec_%02d%s.mp3' % (idx, '' if j == 0 else 'b'))
                parts.append(('— ' + t) if k == 'speech' else t)
                vwho.append(who if (k == 'speech' and who) else 'narr')
            raw.append({'tx': ' — '.join(parts), 'vo': vos,
                        'vtx': parts, 'vwho': vwho})
            continue
        tx = p
        # реплика, продолжающаяся после авторской вставки, начинается со строчной —
        # ставим тире, иначе страница выглядит обрывком («я не могу принять…»)
        if kind == 'speech' and tx[:1].islower():
            tx = '— ' + tx
        tx = re.sub(r'(?<=[а-яё])\.(?=[А-ЯЁ])', '. ', tx)   # «взглянуть.С потухшим»
        pg = {'tx': tx, 'vo': 'audio/vo/rec_%02d.mp3' % len(raw)}
        if kind == 'speech' and who:
            pg['who'] = who
            pg['name'] = NAME[who]
        raw.append(pg)


def anchor_index(frag):
    """Номер страницы по фрагменту её текста (якорь для эмоций/каста)."""
    for i, pg in enumerate(raw):
        if frag in pg['tx']:
            return i
    raise SystemExit('не найден якорь: %r' % frag)


edict = {}
for frag, who, em in EMO_ANCHOR:
    edict[anchor_index(frag)] = (who, em)
cdict = {}
for frag, side, who, em in CAST_ANCHOR:
    cdict[anchor_index(frag)] = {side: (who, em)}

# 2) каст и эмоции по страницам (детерминированно, устойчиво при листании назад)
lside = rside = None
for i, pg in enumerate(raw):
    ev = cdict.get(i)
    if ev:
        if 'l' in ev:
            lside = None if ev['l'][0] == '-' else (list(ev['l']) if ev['l'][0] in CHARS_AVAIL else lside)
        if 'r' in ev:
            rside = None if ev['r'][0] == '-' else (list(ev['r']) if ev['r'][0] in CHARS_AVAIL else rside)
    e = edict.get(i)
    if e:
        who, em = e
        if lside and lside[0] == who: lside = [lside[0], em]
        if rside and rside[0] == who: rside = [rside[0], em]
    cast = {}
    if lside: cast['l'] = lside
    if rside: cast['r'] = rside
    # подсветка говорящего — только на странице с прямой речью: иначе закадровый
    # текст «подсвечивал» персонажа, которого на сцене нет
    if pg.get('who'):
        cast['speak'] = pg['who']
    pg['cast'] = cast

# 3) две сцены вместо одного узла: флешбэк в кабинете и приёмная.
# Нужно для перебивки на стыке (раньше фон щёлкал посреди абзаца, а музыка рвалась).
cut = anchor_index('Сегодня первыми кандидатами')
flash, present = raw[:cut], raw[cut:]

# CG-страница: расскаянный кадр «сникшая Екатерина» (вариант А, выбор Ивана
# 2026-10-24) заменяет фон+спрайты. Спрайты убираем: они уже в самом кадре.
# CG-ДИАПАЗОНОМ (правка Ивана 2026-10-25): кадр держится от якоря начала до якоря конца
# включительно, а не одну страницу. Внутри диапазона спрайты не рисуем — они уже в кадре.
#   rec_35 — P4 v2: «Сергей потер переносицу» → «При всех наших технических возможностях»
#            (новый кабинет, форма Сергея со спрайта, весна за окном)
#   rec_48 — «сникшая Екатерина» → «я не могу принять у вас документы» (было только 1 стр.)
CG_RANGES = [
    ('Сергей потер переносицу', 'При всех наших технических возможностях', 'rec_35'),
    ('На посетительницу больно было взглянуть', 'я не могу принять у вас документы', 'rec_48'),
]
for _a, _b, _name in CG_RANGES:
    i0, i1 = anchor_index(_a), anchor_index(_b)
    if i1 < i0:
        raise SystemExit('CG-диапазон задом наперёд: %r..%r' % (_a, _b))
    hit = 0
    for _i in range(i0, i1 + 1):
        if _i < cut:
            continue                      # CG-точки — только в приёмной, не во флешбэке
        _pg = present[_i - cut]
        _pg['bg'] = 'img/cg/' + _name + CLIENT_EXT
        _pg['cast'] = {}
        _pg['cg'] = True
        hit += 1
    if not hit:
        raise SystemExit('CG-диапазон не попал в приёмную: %r..%r' % (_a, _b))
    print('CG %s: страниц %d (%r .. %r)' % (_name, hit, _a[:28], _b[:28]))

nodes.append({'t': 'scene', 'id': 'starik', 'bg': 'img/bg/cabinet' + CLIENT_EXT,
              'music': 'reception', 'trans': 'fade', 'pages': flash})
nodes.append({'t': 'scene', 'id': 'reception', 'bg': 'img/bg/reception' + CLIENT_EXT,
              'music': 'reception', 'pages': present})


# ---------------------------------------------------- СЦЕНА «АЛЛЕЯ У ВОРОТ»
# story.txt строки 71..121: Екатерина выходит из приёмной и находит на скамейке поэта,
# которого Лихнецкий только что завернул. Разбивка страниц — ТЕМ ЖЕ кодом, что и
# приёмная (_text_seg.segments/pages_of), чтобы подстрочник и озвучка совпадали.
def _mk_pages(pars, speak, prefix):
    """Абзацы → страницы с говорящими; имя mp3 = <prefix>_NN.mp3 (как rec_NN).

    `vof` — ПЛАН озвучки (какие файлы должны быть), `vo` — только реально существующие:
    пока файл не записан, движок его не просит (иначе 404 в консоли и красный
    регресс «js-ошибок нет»). После записи достаточно пересобрать — `vo` появится сам.
    """
    def _exist(rel):
        return os.path.exists(os.path.join(VN2, rel))

    out = []
    for n in sorted(pars):
        who = speak.get(n, '')
        for kind, p in pages_of(segments(pars[n]), 2):
            if kind == 'mix':
                idx = len(out)
                vos, parts, vwho = [], [], []
                for j, (k, t) in enumerate(p):
                    t = re.sub(r'(?<=[а-яё])\.(?=[А-ЯЁ])', '. ', t)
                    vos.append('audio/vo/%s_%02d%s.mp3' % (prefix, idx, '' if j == 0 else 'b'))
                    parts.append(('— ' + t) if k == 'speech' else t)
                    vwho.append(who if (k == 'speech' and who) else 'narr')
                pg = {'tx': ' — '.join(parts), 'vof': vos, 'vtx': parts, 'vwho': vwho}
                _have = [v for v in vos if _exist(v)]
                if _have:
                    pg['vo'] = _have
                out.append(pg)
                continue
            tx = p
            if kind == 'speech' and tx[:1].islower():
                tx = '— ' + tx
            tx = re.sub(r'(?<=[а-яё])\.(?=[А-ЯЁ])', '. ', tx)
            name = 'audio/vo/%s_%02d.mp3' % (prefix, len(out))
            pg = {'tx': tx, 'vof': name}
            if _exist(name):
                pg['vo'] = name
            if kind == 'speech' and who:
                pg['who'] = who
                pg['name'] = NAME[who]
            out.append(pg)
    return out


ALLEY_SPEAK = {75: 'Екатерина', 79: 'Екатерина', 85: 'Екатерина', 89: 'Поэт',
               91: 'Екатерина', 95: 'Поэт', 97: 'Екатерина', 99: 'Поэт',
               103: 'Екатерина', 105: 'Поэт', 107: 'Екатерина', 109: 'Поэт',
               111: 'Екатерина', 115: 'Екатерина', 119: 'Екатерина'}
alley_par = {n: L[n] for n in range(71, 122)
             if L.get(n) and not L[n].startswith('*')}
raw2 = _mk_pages(alley_par, ALLEY_SPEAK, 'al')


def _anchor2(frag):
    for i, pg in enumerate(raw2):
        if frag in pg['tx']:
            return i
    raise SystemExit('якорь сцены «аллея» не найден: %r' % frag)


# состав: (якорь, сторона, кто, эмоция); кто '-' — убрать спрайт.
# 2026-11-05 Иван: поэт теперь СЛЕВА — он сидит на скамейке у края аллеи (как и в тексте:
# «на скамейке между зелёных еловых лап»), Екатерина стоит на дороге справа.
ALLEY_CAST = [
    ('Расстроенная Екатерина Ивановна вышла', 'r', 'Екатерина', 'sad'),
    ('Недалеко от кованых ажурных ворот', 'r', 'Екатерина', 'neutral'),
    ('Недалеко от кованых ажурных ворот', 'l', 'Поэт (на скамейке)', 'upset'),
    ('Юноша еще долго сидел на скамейке', 'r', '-', ''),
]
ALLEY_EMO = [
    ('Екатерина Ивановна улыбнулась и стала искать', 'Екатерина', 'smile'),
    ('Юноша отнял лицо от ладоней', 'Поэт (на скамейке)', 'neutral'),
    ('Тот что-то неразборчиво буркнул', 'Поэт (на скамейке)', 'upset'),
    ('Поэт нерешительно дернул плечом', 'Поэт (на скамейке)', 'sullen'),
    ('Наконец оторвавшись от ладоней', 'Поэт (на скамейке)', 'neutral'),
    ('юноша покраснел и отвернулся', 'Поэт (на скамейке)', 'shy'),
    ('Что это?', 'Поэт (на скамейке)', 'interested'),
    ('Зачем он мне', 'Поэт (на скамейке)', 'sullen'),
    ('Поэт поджал губы', 'Поэт (на скамейке)', 'sullen'),
    ('потрепала его по голове', 'Поэт (на скамейке)', 'smile'),
]
_cdict2 = {}
for frag, side, who, em in ALLEY_CAST:
    _cdict2.setdefault(_anchor2(frag), {})[side] = (who, em)
_edict2 = {}
for frag, who, em in ALLEY_EMO:
    _edict2[_anchor2(frag)] = (who, em)

_l2 = _r2 = None
for i, pg in enumerate(raw2):
    ev = _cdict2.get(i)
    if ev:
        if 'l' in ev:
            _l2 = None if ev['l'][0] == '-' else (list(ev['l']) if ev['l'][0] in CHARS_AVAIL else _l2)
        if 'r' in ev:
            _r2 = None if ev['r'][0] == '-' else (list(ev['r']) if ev['r'][0] in CHARS_AVAIL else _r2)
    e = _edict2.get(i)
    if e:
        who, em = e
        if _l2 and _l2[0] == who:
            _l2 = [_l2[0], em]
        if _r2 and _r2[0] == who:
            _r2 = [_r2[0], em]
    cast = {}
    if _l2:
        cast['l'] = _l2
    if _r2:
        cast['r'] = _r2
    if pg.get('who'):
        cast['speak'] = pg['who']
    pg['cast'] = cast

_cut2 = _anchor2('Недалеко от кованых ажурных ворот')
steps_pages, alley_pages = raw2[:_cut2], raw2[_cut2:]
if not steps_pages or not alley_pages:
    raise SystemExit('сцена «аллея»: пустая часть (steps %d, alley %d)'
                     % (len(steps_pages), len(alley_pages)))

# CG на пиковую страницу «— Муза, — юноша покраснел и отвернулся» (решение Ивана
# 2026-11-04: «давай попробуем CG на музу»): кадр заменяет фон+спрайты на ОДНОЙ странице.
# Готча: _anchor2 считает по ВСЕМУ raw2, а alley_pages = raw2[_cut2:] — индекс надо сдвинуть.
_muza = _anchor2('юноша покраснел и отвернулся') - _cut2
if not (0 <= _muza < len(alley_pages)):
    raise SystemExit('CG «Муза»: индекс вне узла (%d при %d страницах)' % (_muza, len(alley_pages)))
alley_pages[_muza]['bg'] = 'img/cg/al_muza' + CLIENT_EXT
alley_pages[_muza]['cast'] = {}
alley_pages[_muza]['cg'] = True
print('CG al_muza: страница %d сцены «аллея» (%r)' % (_muza, alley_pages[_muza]['tx'][:34]))
# перебивка на «* * *» перед выходом из приёмной — тот же длинный переход, что у кабинета
nodes.append({'t': 'scene', 'id': 'steps', 'bg': 'img/bg/steps' + CLIENT_EXT,
              'music': 'reception', 'trans': 'fade', 'pages': steps_pages})
nodes.append({'t': 'scene', 'id': 'alley', 'bg': 'img/bg/alley' + CLIENT_EXT,
              'music': 'alley',
              # скамейка — статичный предмет сцены: не дрожит и не масштабируется со спрайтом
              'prop': {'src': 'img/prop/bench.webp', 'left': '22%', 'bottom': '-6%', 'h': '59%'},
              'pages': alley_pages})
print('сцена «аллея»: steps %d стр., alley %d стр.' % (len(steps_pages), len(alley_pages)))


# ---------------------------------------------------------------- титры (благодарности)
# Только подтверждённые имена. Сюда же дописывать новых людей по мере находки.
CREDITS_TBD = [
    # «Фоны, 2016» — художница, рисовавшая фоны для билда 2016 (имя ищется)
    # ещё два человека из команды 2016 — след потерян (имена ищутся)
]
CREDITS = [
    {'h': 'Рассказ',
     'rows': ['Автор|Александр «Котобус» Горбов']},
    {'h': 'Первый билд · 2016',
     'rows': ['Спрайты персонажей|Алексей Стребков «Leonzo»'],
     'notes': ['Отдельное спасибо Алексею за спрайты 2016 года']},
    {'h': 'Эпизод 1 · 2026',
     'rows': ['Кадры и графика|flux-2 · gpt-image-2 · nano-banana-2.1',
              'Закадр и Лихнецкий|Gemini TTS «Charon»',
              'Старик|Gemini TTS «Fenrir»',
              'Екатерина Ивановна|ElevenLabs v4 «Charlotte»',
              'Музыка|Lyria 3.5',
              'Жетон-значок|собственная 3D-отрисовка']},
    # Без придуманных должностей: никаких «режиссёр/продюсер» — только имена
    # и то, что действительно сделано (уточнено Иваном 2026-10-24).
    {'h': 'Над эпизодом работали',
     'rows': ['Иван Карпухин · piroman99', 'nanobot 🐈'],
     'notes': ['Отбор кадров и решений — Иван; кадры, озвучка и движок — nanobot']},
]

data = {
    'title': 'ЗАРЯНКА',
    'episode': 'Эпизод 1 · «Пролог. Приёмная комиссия»',
    'byline': 'по рассказу Александра «Котобус» Горбова',
    'credits': CREDITS,
    'voVer': VO_VER,
    'emblemVer': EMBLEM_VER,
    'music': {'prolog': '../assets/audio/sketch/prolog_bed_soft_0.mp3',
              'reception': '../assets/audio/sketch/vn_reception_soft_0.mp3',
              # сцена «аллея» — своя тема весенней улицы (правка Ивана 2026-11-05, п.5):
              # тёплая тема + фон улицы (капель, птицы, ветер в елях).
              # Варианты рядом: alley_bed.mp3 (только тема), alley_amb.mp3 (только улица).
               'alley': '../assets/audio/sketch/alley_mix.mp3?v=2'},
    'chars': CHARS_AVAIL,
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
