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

PLATE_FILE = {'s1': 'prologfin_s1_b_0.jpg',   # B: котобус мелом ВПЕЧЁН в кадр (не наклейка)
              's2': 'prologfin2_s2a_0.jpg',    # цех сборки (номер 410 отменён, космодром не берём)
              's3': 'prologfin3_s3_d_0.jpg',  # D: светлый зал, озабоченные-но-не-грустные лица
              's4': 'prologfin4_s4_d_0.jpg',  # D: комната 2061, станция у Марса на экране, без букв
              's5': 'prologfin6_s5_a_0.jpg',  # A: вымышленный Верховный Совет «Триумф», день, без ракеты
              's6': 's6_gpt3_b_0.png',   # B (выбран Иваном 2026-10-17): весна, ворота Звёздного
                                          # городка, очередь умеренная, пара Женя+Семён, лица нейтральные
              's7': 's7b_gpt_a_0.png'}   # A (выбран Иваном 2026-10-18): камера с крыльца приёмной,
                                          # ступени вниз, еловая аллея, очередь 50-70 чел, ворот НЕТ,
                                          # Звёздный городок (лес вплотную, низкие корпуса)


def F(p, s):
    return ImageFont.truetype(p, s)


def load_plate(name):
    im = Image.open(os.path.join(GEN, PLATE_FILE[name])).convert('RGB')
    return im.resize((FW, FH), Image.LANCZOS)


def soft(base, box, color, alpha, blur=16):
    ov = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(box, radius=20, fill=tuple(color) + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB')


def tag(base, txt):
    d = ImageDraw.Draw(base)
    x1 = 70 + 26 + int(len(txt) * 15)
    d.rectangle([70, 70, x1, 128], fill=(0, 0, 0))
    d.text((90, 82), txt, font=F(LATO_B, 30), fill=(232, 180, 120))
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
        # котобус мелом уже ВПЕЧЁН в плашку flux-2; сверху — только текстовый слой
        base = soft(base, (620, 990, 1780, 1120), (6, 8, 14), 175, blur=18)
        ImageDraw.Draw(base).text((1200, 1055), 'МАРС — ДЕЛО ОБЩЕЕ?',
                                  font=F(GOTHIC, 58), fill=(238, 214, 150), anchor='mm')
        base = tag(base, 'ПОДВОРОТНЯ')
    elif n == 's2':
        base = tag(base, 'ЦЕХ · СБОРКА')
    elif n == 's3':
        base = soft(base, (620, 330, 1780, 1010), (6, 8, 14), 150, blur=26)
        d = ImageDraw.Draw(base)
        d.text((1200, 430), '«МАРС —', font=F(GOTHIC, 108), fill=CREAM, anchor='ma')
        d.text((1200, 560), 'ДЕЛО ОБЩЕЕ?»', font=F(GOTHIC, 108), fill=CREAM, anchor='ma')
        d.text((1200, 720), '«ОБЩЕЕ!»', font=F(GOTHIC, 86), fill=GREEN, anchor='ma')
        d.text((1200, 860), 'а что же обычных людей нет?', font=F(LATO_B, 52), fill=CREAM, anchor='ma')
        base = tag(base, 'ЗАЛ · ВОПРОС')
    elif n == 's4':
        # ПРАВКА 2026-10-17 (Иван): сначала подпись уходила под подстрочник при наезде
        # (scale 1.0->1.5, origin x .44 y .30) — поднята к телевизору. Затем «слишком мелко» —
        # кегль подгоняется ПОД ШИРИНУ ЭКРАНА ТВ (замер по s4.png, 2400-пространство:
        # экран ТВ x 733..1650 (ширина 917), y 197..666).
        TXT = 'а что же обычных людей нет?'
        TV_L, TV_R, TV_B = 733, 1650, 666      # экран ТВ в 2400x1350
        TARGET = int((TV_R - TV_L) * 0.94)      # 94% ширины экрана -> поля по краям
        size = 40
        d = ImageDraw.Draw(base)
        while d.textlength(TXT, font=F(LATO_B, size)) < TARGET:
            size += 1
        fnt = F(LATO_B, size)
        tw = d.textlength(TXT, font=fnt)
        cx, by0 = (TV_L + TV_R) // 2, TV_B + 18   # по центру экрана, чуть ниже кромки
        pad_x, pad_y = 22, 16
        bx0, bx1 = int(cx - tw / 2 - pad_x), int(cx + tw / 2 + pad_x)
        by1 = int(by0 + size + 2 * pad_y)
        base = soft(base, (bx0, by0, bx1, by1), (4, 5, 10), 180, blur=14)
        ImageDraw.Draw(base).text((cx, (by0 + by1) / 2), TXT, font=fnt, fill=CREAM, anchor='mm')
        print('   s4 caption: size=%d tw=%.0f (экран %d) band=%s' % (size, tw, TV_R - TV_L,
                                                               (bx0, by0, bx1, by1)))
        base = tag(base, 'ВИДЕОРОЛИК · НАРЕЗКА')
    elif n == 's5':
        # ВАРИАНТ A (выбран заказчиком 2026-10-17): полоса лозунга на фасаде.
        # Геометрия и кегли = лист review_97_s5_banner_ab.png (_prolog_s5_banner_ab.py, CONF['A']).
        band = (300, 500, 2100, 780)
        base = soft(base, band, (168, 40, 34), 232, blur=10)
        d = ImageDraw.Draw(base)
        cx, y0 = (band[0] + band[2]) / 2, band[1]
        d.text((cx, y0 + 50), 'МАРС — ДЕЛО ОБЩЕЕ!', font=F(GOTHIC, 76), fill=CREAM, anchor='ma')
        d.text((cx, y0 + 142), 'ДАЁШЬ МАРС ДЛЯ ВСЕХ!', font=F(GOTHIC, 62), fill=(252, 226, 170), anchor='ma')
        chip = (600, 830, 1320, 920)
        base = soft(base, chip, (6, 8, 14), 150, blur=14)
        ImageDraw.Draw(base).text(((chip[0] + chip[2]) / 2, (chip[1] + chip[3]) / 2),
                                  '2 МЕСТА «С УЛИЦЫ»', font=F(GOTHIC, 46), fill=(255, 210, 120), anchor='mm')
        base = tag(base, 'ЛОЗУНГ · СТРАНА')
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
    p = os.path.join(FIN, n + '.png')
    out.save(p)
    print('final', n, '->', os.path.relpath(p, HERE))


ONLY = sys.argv[1:] or ('s1', 's2', 's3', 's4', 's5', 's6', 's7')
for n in ONLY:
    build(n)
print('готово')
