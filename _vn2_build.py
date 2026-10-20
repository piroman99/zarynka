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
import os, json, re, shutil, sys
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
    's2': [],
    's3': ['s3_q1', 's3_q2', 's3_q3'],
    's4': ['s4_video', 's4_q'],
    's5': ['s5_posters', 's5_soviet', 's5_seats'],
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
}
for dst, src in CHAR_SRC.items():
    if not os.path.exists(src):
        print('char SKIP (нет источника):', dst)
        continue
    out = cutout(Image.open(src))
    save_client(out, os.path.join(IMG, 'char'), dst.rsplit('.', 1)[0], lossless=False)
    print('char', dst, out.size, out.mode)


# доступные спрайты и эмоции (по фактическим файлам в img/char) — движок
# рисует только то, что есть, и подхватит новые эмоции без правок кода
def char_manifest():
    key_of = {'Сергей': 'sergey', 'Екатерина': 'kate', 'Старик': 'starik'}
    known = ['neutral', 'smile', 'sad', 'concerned', 'stern']
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
    return d


CHARS_AVAIL = char_manifest()

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


def segments(par):
    """Абзац -> [('speech'|'narr', текст)].

    Маркер диалога — «— » в начале абзаца или после , . ? ! … : ;
    (тире ВНУТРИ фразы без знака перед ним — обычное тире, не маркер).
    Авторская вставка ВНУТРИ реплики — ОТДЕЛЬНЫЙ сегмент (её читает закадр).
    Старое правило «вставка на запятой = пауза внутри реплики» давало баг:
    персонаж читал авторский текст, страница обрывалась на полуслове, а
    следующая начиналась со строчной — «озвучка разъехалась с текстом».
    Правильно: каждый сегмент — своя страница, голос по роли
    (Иван, 2026-10-20: «озвучка разъехалась с текстом, повторы какие-то»).
    """
    starts = []
    for m in re.finditer(r'—\s', par):
        i = m.start()
        if i == 0:
            starts.append((i, m.end()))
            continue
        prev = par[:i].rstrip()
        if prev and prev[-1] in ',.?!…:;':
            starts.append((i, m.end()))
    if not starts:
        return [('narr', par.strip())]
    out = []
    if starts[0][0] > 0:
        head = par[:starts[0][0]].strip()
        if head:
            out.append(('narr', head))
    for k, (i, end) in enumerate(starts):
        stop = starts[k + 1][0] if k + 1 < len(starts) else len(par)
        seg = par[end:stop].strip()
        if seg:
            out.append(('speech' if k % 2 == 0 else 'narr', seg))
    return out


def pages_of(segs, maxn=2):
    """Сегменты -> страницы по 1-2 предложения, НИКОГДА не смешивая
    реплику и авторский текст в одной странице."""
    out = []
    for kind, tx in segs:
        cur = []
        for s in [x.strip() for x in SENT.split(tx) if x.strip()]:
            cur.append(s)
            if len(cur) >= maxn:
                out.append((kind, ' '.join(cur))); cur = []
        if cur:
            out.append((kind, ' '.join(cur)))
    return out


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


nodes = []
nodes.append({'t': 'title'})
nodes.append({'t': 'znak', 'video': '../out/znak3d_rot.mp4',
              'caption': 'Зарянка'})

# пролог: кадр + страницы дословного текста + закадр (существующий vo_prolog2)
# камера «двухбит одним кадром» — плавный наезд без склейки (S4 → Марс на панели)
PROLOG_CAM = {'s4': {'from': 1.0, 'to': 1.5, 'x': 0.44, 'y': 0.30, 'hold': 0.9, 'dur': 3.4}}
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
            pgs.append({'tx': p, 'vo': f'audio/vo/{name}_{len(pgs):02d}.mp3'})
    for pg in pgs:
        if name in PROLOG_CAM:
            pg['cam'] = PROLOG_CAM[name]
    node = {'t': 'scene', 'id': name, 'bg': f'img/prolog/{name}{CLIENT_EXT}',
            'music': 'prolog', 'pages': pgs}
    nodes.append(node)

# приёмная: фон + спрайты + дословный текст, с говорящими
SPEAK = {15: 'Старик', 23: 'Сергей', 25: 'Екатерина', 29: 'Сергей', 31: 'Екатерина',
         33: 'Сергей', 37: 'Сергей', 41: 'Сергей', 43: 'Екатерина', 45: 'Сергей',
         47: 'Екатерина', 49: 'Сергей', 51: 'Екатерина', 53: 'Сергей', 57: 'Сергей',
         61: 'Сергей', 63: 'Екатерина', 65: 'Сергей', 67: 'Екатерина'}
NAME = {'Сергей': 'Лихнецкий Сергей', 'Екатерина': 'Екатерина Ивановна',
        'Старик': 'Старик'}

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
# Флешбэк в кабинете Старика (Сергей попался под горячую руку) → приёмная: Сергей один,
# потом входит Екатерина.
CAST_ANCHOR = [
    ('Лихнецкому не повезло', 'l', 'Старик', 'stern'),
    ('Так и пришлось долгих два месяца', 'l', 'Сергей', 'neutral'),
    ('Образовалась пауза', 'r', 'Екатерина', 'neutral'),
]

# 1) текст + говорящие: реплика и авторский текст разведены по СЕГМЕНТАМ
# (старый баг: голос ставился на весь абзац, и авторский текст между фразами
#  Екатерины читался её же голосом)
raw = []
for n in sorted(reception_par):
    who = SPEAK.get(n, '')
    for kind, p in pages_of(segments(reception_par[n]), 2):
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
        if 'l' in ev and ev['l'][0] in CHARS_AVAIL: lside = list(ev['l'])
        if 'r' in ev and ev['r'][0] in CHARS_AVAIL: rside = list(ev['r'])
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
nodes.append({'t': 'scene', 'id': 'starik', 'bg': 'img/bg/cabinet' + CLIENT_EXT,
              'music': 'reception', 'pages': flash})
nodes.append({'t': 'scene', 'id': 'reception', 'bg': 'img/bg/reception' + CLIENT_EXT,
              'music': 'reception', 'pages': present})


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
]

data = {
    'title': 'ЗАРЯНКА',
    'episode': 'Эпизод 1 · «Пролог. Приёмная комиссия»',
    'byline': 'по рассказу Александра «Котобус» Горбова',
    'credits': CREDITS,
    'music': {'prolog': '../assets/audio/sketch/prolog_bed_soft_0.mp3',
              'reception': '../assets/audio/sketch/vn_reception_soft_0.mp3'},
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
