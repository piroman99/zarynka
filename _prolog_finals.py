# -*- coding: utf-8 -*-
"""ФИНАЛЬНЫЕ КАДРЫ ПРОЛОГА (vn2) — фотореалистичные плашки flux-2 + документарный текстовый слой.

Идея: моковые кадры были плоскими (для аниматика). Для VN под каждый узел S1..S7
берём фото-плашку в стиле «кинохроника 2061» и поверх кладём ТОЛЬКО текстовую
хроникальную графику (метка кадра, реплика-вопрос, лозунг, часы 06:07, плакат вахты) —
в позициях, не зависящих от композиции фото (мягкие затемнения-скримы под текст).

Результат -> assets/final/prolog/sN.png (1920x1080, БЕЗ грейда — грейд делает _vn2_build.py).
Плашки кэшируются: если assets/gen/prologfin_sN_0.jpg есть — повторно не генерим (0 ₽).
S1/S2 переиспользуют уже сгенерированные пробы flux-2.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

GEN = os.path.join(HERE, 'assets', 'gen')
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')
os.makedirs(FIN, exist_ok=True)

FW, FH = 2400, 1350
OUTW, OUTH = 1920, 1080
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
GOLD = (226, 186, 104)
CREAM = (246, 238, 222)
GREEN = (126, 214, 128)
RED = (176, 44, 38)

CHRON = ("ретро-футуристическая документальная кинохроника альтернативного 2061 года, "
         "кадр из фильма, 16:9, киноплёнка с зерном и лёгкими царапинами, приглушённая "
         "холодная палитра, живописный фотореализм. НЕ мультфильм, НЕ аниме, НЕ 3D-рендер, "
         "НИКАКОГО текста, надписей, букв, цифр, логотипов и водяных знаков.")

# ---- плашки, которые ещё надо сгенерировать (S1, S2 уже есть) ------------
PLATES = {
    # S3/S4/S5 — СТАРЫЕ описания удалены: плашки уже закрыты (prologfin3_s3_d / prologfin4_s4_d /
    # prologfin6_s5_a). Держать их здесь опасно — при отсутствии файла скрипт перегенерит СТАРЫЙ
    # дизайн и сожжёт деньги (так и вышло 2026-10-14: −4.74 ₽). Новые кадры генерим отдельными
    # скриптами (_prolog_s3_*, _prolog_s4_v2, _prolog_s5_v3).
    # S6 — старое описание (очередь к закрытой двери, синие сумерки) УДАЛЕНО: забраковано
    # («это в банк, девяностые»). Новый кадр = отдельный скрипт _prolog_s6_a.py.
    # S7 — старое описание (проходная, КПП, вахтёр, туман) УДАЛЕНО: кадр переделан
    # 2026-10-18 («не та местность», «лишние ворота», «вдвое меньше народа»).
    # Новый кадр = _prolog_s7b_a.py.
}

for n, desc in PLATES.items():
    out = os.path.join(GEN, 'prologfin_%s_0.jpg' % n)
    if os.path.exists(out):
        print('plate %s: есть (кэш) %s' % (n, os.path.getsize(out)))
        continue
    prompt = desc + "\n\nСТИЛЬ: " + CHRON
    files, st = pv.generate_to_files("flux-2", prompt, {"aspect_ratio": "16:9", "resolution": "2K"},
                                     outdir="assets/gen", name='prologfin_%s' % n, max_price_rub=12)
    print('plate %s -> %s  price=%s' % (n, os.path.relpath(files[0], HERE), st.get('priceRub')))

# СТЕНА Звёздного городка (кадр S1, страница 1) — выбор варианта ОДНОЙ строкой:
#   s1wall_a — крупно, фрунтально, у стены ведро и тряпка
#   s1wall_b — шире: угол двора, весенние тени, фигура спиной
# Кадр без наших букв: граффити «МАРС — ДЕЛО ОБЩЕЕ» нарисовано моделью (gpt-image-2).
WALL_PLATE = os.environ.get('WALL_PLATE', 's1wall_b__gpt-image-2_0.png')

PLATE_FILE = {'s1': 'prologfin_s1_b_0.jpg',   # B: котобус мелом ВПЕЧЁН в кадр (не наклейка);
                                             # с 2026-11-04 — ВТОРАЯ страница кадра s1
              's2': 'prologfin2_s2a_0.jpg',    # цех сборки (номер 410 отменён, космодром не берём)
              's3': 'prologfin3_s3_d_0.jpg',  # D: светлый зал, озабоченные-но-не-грустные лица
              's4': 'prologfin4_s4_d_0.jpg',  # D: комната 2061, станция у Марса на экране, без букв
              's5': 'prologfin6_s5_a_0.jpg',  # A: вымышленный Верховный Совет «Триумф», день, без ракеты
              's5a': 's5a_b__gpt-image-2_0.png',  # кадр 11 (2026-11-01, Иван выбрал вариант B):
                                                 # общий план площади, плакатные тумбы; плакаты ПУСТЫЕ
              's6': 's6_gpt3_b_0.png',   # B (выбран Иваном 2026-10-17): весна, ворота Звёздного
                                          # городка, очередь умеренная, пара Женя+Семён, лица нейтральные
              's7': 's7b_gpt_a_0.png'}   # A (выбран Иваном 2026-10-18): камера с крыльца приёмной,
                                          # ступени вниз, еловая аллея, очередь 50-70 чел, ворот НЕТ,
                                          # Звёздный городок (лес вплотную, низкие корпуса)


def F(p, s):
    return ImageFont.truetype(p, s)


def load_plate(name):
    fn = WALL_PLATE if name == 's1wall' else PLATE_FILE[name]
    im = Image.open(os.path.join(GEN, fn)).convert('RGB')
    return im.resize((FW, FH), Image.LANCZOS)


def soft(base, box, color, alpha, blur=16):
    ov = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(box, radius=20, fill=tuple(color) + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB')


def tag(base, txt):
    # Ширина плашки — по РЕАЛЬНОЙ ширине текста (было len*15 → текст вылезал за
    # плашку на 3–46 px во всех кадрах, «ПЛОЩАДЬ · ЛОЗУНГ» обрезалась).
    d = ImageDraw.Draw(base)
    f = F(LATO_B, 30)
    x1 = 90 + int(d.textlength(txt, font=f)) + 20
    d.rectangle([70, 70, x1, 128], fill=(0, 0, 0))
    d.text((90, 82), txt, font=f, fill=(232, 180, 120))
    return base


# ДИЕГЕТИЧЕСКОЕ ТАБЛО (правка Ивана 2026-10-17): плавающие часы «06:07» убраны как
# немотивированные. Время имеет смысл только как реальный предмет в кадре — электронное
# табло на проходной. None = без часов; (x0,y0,x1,y1) в пространстве 2400x1350.
CLOCK = None
CLOCK_TEXT = '06:07'


def draw_clock(base, x0, y0, x1, y1):
    import _s6_clock_ab as _C
    return _C.clock(base, (x0, y0, x1, y1), text=CLOCK_TEXT)


def vignette(im, strength=0.75):
    w, h = im.size
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).ellipse([-w * 0.22, -h * 0.30, w * 1.22, h * 1.30], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w // 10))
    dark = Image.new('RGB', (w, h), (0, 0, 0))
    return Image.composite(im, dark, Image.eval(mask, lambda v: 255 - int((255 - v) * strength)))


def build(n):
    base = load_plate(n)
    if n == 's1':
        # 2026-11-04 (решение Ивана, развилка A): это теперь ВТОРАЯ страница кадра s1
        # («поймать умника в темной подворотне»). Подпись «МАРС — ДЕЛО ОБЩЕЕ?» снята:
        # сама надпись ушла на первую страницу — в граффити на стене (кадр s1a).
        # Котобус мелом остаётся — он ВПЕЧЁН в плашку flux-2.
        base = tag(base, 'ПОДВОРОТНЯ')
    elif n == 's1wall':
        # Первая страница кадра s1: стена Звёздного городка, полустёртое граффити.
        # Своих букв НЕ добавляем — надпись в кадре нарисована моделью.
        base = tag(base, 'ЗВЁЗДНЫЙ ГОРОДОК')
    elif n == 's2':
        base = tag(base, 'ЦЕХ · СБОРКА')
    elif n == 's3':
        # 2026-11-01 (бриф 9-12): плашка и строки УБРАНЫ из PNG — они ушли в титр-слой
        # движка (pg.ovl в _vn2_build.py) и появляются ПО СТРАНИЦАМ. Здесь только метка.
        base = tag(base, 'ЗАЛ · ВОПРОС')
    elif n == 's4':
        # 2026-11-01 (вариант B по кадру 10): подпись «а что же обычных людей нет?» СНЯТА
        # с экрана панели — теперь это титр-слой движка (pg.ovl), по фразе. Геометрия
        # подписи сохранена в замечании: кегль 61, полоса (738,684,1644,777).
        base = tag(base, 'РОЛИК · НА СКОРУЮ РУКУ')
    elif n == 's5a':
        # КАДР 11 (2026-11-01, развилка «место» = вариант (ii): городская площадь с плакатными
        # тумбами). Плакаты в кадре ПУСТЫЕ — полоса лозунга живёт в титр-слое движка (pg.ovl)
        # и появляется по фразе. Здесь только метка.
        base = tag(base, 'ПЛОЩАДЬ · ЛОЗУНГ')
    elif n == 's5':
        # 2026-11-01 (кадр 12 = s5b, 0 ₽): полоса лозунга и старый чип СНЯТЫ с фасада.
        # Лозунг теперь на кадре 11 (s5a), чип «ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ» — в титр-слое
        # движка по фразе. Геометрия чипа для ovl: (560,830,1360,920), GOTHIC 46.
        base = tag(base, 'ВЕРХОВНЫЙ СОВЕТ')
    elif n == 's6':
        # ПРАВКА 2026-10-17 (Иван): плавающие часы «06:07» убраны — «не к селу не к городу».
        # Время имеет смысл только ДИЕГЕТИЧЕСКИ (электронное табло в кадре), см. CLOCK ниже.
        if CLOCK:
            base = draw_clock(base, *CLOCK)
        base = tag(base, 'ОЧЕРЕДЬ · ПРИЁМНАЯ')
    elif n == 's7':
        # ПРАВКА 2026-10-18 (Иван): плавающий плакат «ТЫ НЕ ПРОЙДЁШЬ!» убран.
        # Затем: «не хочу такую табличку, слишком заметная» → тихий вариант A:
        # вдвое меньше, корпус в тон стене (стена = 162,146,136), тёмная гравировка
        # без красной эмали. Геометрия стены замерена по кадру (x 0..98, y 0..525 в 1672x941).
        # См. _s7_plaque2.py (STYLES) и PROLOG_FIXES.md.
        import _s7_plaque2
        base = _s7_plaque2.plaque(base, 'a')
        base = tag(base, 'ПРОХОДНАЯ · ОЧЕРЕДЬ')
    out = vignette(base).resize((OUTW, OUTH), Image.LANCZOS)
    # s1wall — первая страница кадра s1: в движке живёт как отдельный кадр img/prolog/s1a
    p = os.path.join(FIN, ('s1a' if n == 's1wall' else n) + '.png')
    out.save(p)
    print('final', n, '->', os.path.relpath(p, HERE))


ONLY = sys.argv[1:] or ('s1', 's1wall', 's3', 's4', 's5', 's5a', 's6', 's7')
for n in ONLY:
    build(n)
print('готово')
