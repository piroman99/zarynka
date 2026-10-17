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
    's6': ("Раннее утро, синие предрассветные сумерки: длинная плотная очередь людей перед "
           "закрытой входной дверью административного здания в Звёздном городке; люди стоят "
           "вплотную, вид со спины, в куртках и шапках; мокрый асфальт, фонари, туман, "
           "ощущение очереди с самой ночи."),
    's7': ("Проходная космического городка 2061 года: длинная очередь у контрольно-пропускного "
           "пункта, кирпичная стена, будка с турникетом и стеклянным окном, вахтёр в форме. "
           "В очереди со спин, лиц не видно: молодая пара держится за руки — женщина в очках с "
           "книгой, мужчина отвёрнут; рядом человек ведёт двух небольших собак на поводке; "
           "мальчик на плечах отца держит игрушечную ракету. Утро, туман, приглушённый свет."),
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
              's6': 'prologfin_s6_0.jpg',
              's7': 'prologfin_s7_0.jpg'}


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
        base = tag(base, 'ПОДВОРОТНЯ · 06:07')
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
        base = soft(base, (360, 880, 2040, 1030), (4, 5, 10), 190, blur=18)
        ImageDraw.Draw(base).text((1200, 956), 'а что же обычных людей нет?',
                                  font=F(LATO_B, 52), fill=CREAM, anchor='mm')
        base = tag(base, 'ВИДЕОРОЛИК · НАРЕЗКА')
    elif n == 's5':
        base = soft(base, (300, 500, 2100, 780), (168, 40, 34), 232, blur=10)
        d = ImageDraw.Draw(base)
        d.text((1200, 580), 'МАРС — ДЕЛО ОБЩЕЕ!', font=F(GOTHIC, 92), fill=CREAM, anchor='ma')
        d.text((1200, 700), 'ДАЁШЬ МАРС ДЛЯ ВСЕХ!', font=F(GOTHIC, 76), fill=(252, 226, 170), anchor='ma')
        base = soft(base, (820, 830, 1580, 920), (6, 8, 14), 150, blur=14)
        ImageDraw.Draw(base).text((1200, 876), '2 МЕСТА «С УЛИЦЫ»', font=F(GOTHIC, 54), fill=(255, 210, 120), anchor='mm')
        base = tag(base, 'ЛОЗУНГ · СТРАНА')
    elif n == 's6':
        base = soft(base, (1880, 84, 2310, 214), (8, 10, 14), 200, blur=12)
        ImageDraw.Draw(base).text((2095, 150), '06:07', font=F(GOTHIC, 72), fill=(238, 176, 84), anchor='mm')
        base = tag(base, 'ОЧЕРЕДЬ · ПРИЁМНАЯ')
    elif n == 's7':
        px0, py0, px1, py1 = 1760, 250, 2250, 640
        base = soft(base, (px0 - 24, py0 - 24, px1 + 24, py1 + 24), (0, 0, 0), 130, blur=18)
        d = ImageDraw.Draw(base)
        d.rectangle([px0, py0, px1, py1], fill=(206, 196, 170), outline=(178, 54, 46), width=10)
        import math as _m
        cx, cy, R = (px0 + px1) / 2, py0 + 52, 30
        star = []
        for k in range(10):
            r = R if k % 2 == 0 else R * 0.42
            a = _m.radians(-90 + 36 * k)
            star.append((cx + r * _m.cos(a), cy + r * _m.sin(a)))
        d.polygon(star, fill=(196, 54, 44))
        d.text((cx, py0 + 160), 'ТЫ НЕ', font=F(GOTHIC, 60), fill=(176, 44, 36), anchor='ma')
        d.text((cx, py0 + 236), 'ПРОЙДЁШЬ!', font=F(GOTHIC, 54), fill=(176, 44, 36), anchor='ma')
        d.text((cx, py0 + 320), 'ВАХТА · ПРИЁМНАЯ', font=F(LATO_B, 24), fill=(120, 96, 60), anchor='ma')
        base = tag(base, 'ПРОХОДНАЯ · ОЧЕРЕДЬ')
    out = vignette(base).resize((OUTW, OUTH), Image.LANCZOS)
    p = os.path.join(FIN, n + '.png')
    out.save(p)
    print('final', n, '->', os.path.relpath(p, HERE))


for n in ('s1', 's2', 's3', 's4', 's5', 's6', 's7'):
    build(n)
print('готово')
