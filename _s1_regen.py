# -*- coding: utf-8 -*-
"""S1 (подворотня): котобус мелом ВПЕЧЬ В КАДР flux-2 (не клеить оверлеем).
Заказчик: бесплатный плоский рисунок выглядит наклейкой (ровный, крупный, лезет
на окно/трубу/фигуру) → генерим кадр с меловым рисунком в самом промпте.
Выход: assets/gen/prologfin_s1_{a,b}_0.jpg + пересборка assets/final/prolog/s1.png
       + лист сравнения assets/review/review_85_s1_baked.png
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

GEN = os.path.join(HERE, 'assets', 'gen')
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')
REV = os.path.join(HERE, 'assets', 'review')
FW, FH = 2400, 1350
OUTW, OUTH = 1920, 1080
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

CHRON = ("ретро-футуристическая документальная кинохроника альтернативного 2061 года, "
         "кадр из фильма, 16:9, киноплёнка с зерном и лёгкими царапинами, приглушённая "
         "холодная палитра, живописный фотореализм. НЕ мультфильм, НЕ аниме, НЕ 3D-рендер, "
         "НИКАКОГО текста, надписей, букв, цифр, логотипов и водяных знаков.")

SCENE = ("Советская глухая подворотня глухой ночью, захламлённый двор: облупленная кирпичная "
         "стена с осыпавшейся штукатуркой, тёмная арка во двор, ржавая водосточная труба, "
         "голая лампочка на проводе тускло светит, покосившиеся мусорные контейнеры, лужа и "
         "чугунный люк на асфальте, одинокий силуэт человека в кепке у стены.")
CHALK = ("На свободном участке кирпичной стены выше человеческого роста — НЕБОЛЬШОЙ неумелый "
         "детский рисунок, нарисованный белым мелом ОТ РУКИ: примитивный толстый улыбающийся "
         "кот с большими ушами, длинным хвостом и множеством лап (кот-автобус), нарисованный "
         "кривыми неровными линиями, местами прерывающимися; мел бледный, слегка осыпавшийся. "
         "Рисунок маленький (занимает небольшую часть стены), неаккуратный, как рисуют дети.")
TAIL = ("Неухоженно, менее аккуратно, чем западный двор, атмосфера тайны, глубокая тень. "
        "Холодная сине-серая палитра.")

# --- генерация двух вариантов -------------------------------------------
prompts = {
    'a': SCENE + ' ' + CHALK + ' ' + TAIL,
    'b': (SCENE + ' На кирпичной стене мелом нарисован кривой неумелый детский многолапый кот '
          '(кот-автобус): большие уши, длинный хвост, несколько лап, схематичные линии, '
          'как будто рисовал ребёнок. Рисунок небольшой, на кирпиче, не на окнах и не на предметах. '
          + TAIL),
}
for k, core in prompts.items():
    out = os.path.join(GEN, 'prologfin_s1_%s_0.jpg' % k)
    if os.path.exists(out):
        print('plate s1_%s: кэш' % k); continue
    files, st = pv.generate_to_files("flux-2", core + "\n\nСТИЛЬ: " + CHRON,
                                     {"aspect_ratio": "16:9", "resolution": "2K"},
                                     outdir="assets/gen", name='prologfin_s1_%s' % k, max_price_rub=12)
    print('plate s1_%s -> %s price=%s' % (k, os.path.relpath(files[0], HERE), st.get('priceRub')))


# --- пересборка финального S1 (как _prolog_finals.build для s1) ----------
def vignette(im, strength=0.75):
    w, h = im.size
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).ellipse([-w * 0.22, -h * 0.30, w * 1.22, h * 1.30], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w // 10))
    dark = Image.new('RGB', (w, h), (0, 0, 0))
    return Image.composite(im, dark, Image.eval(mask, lambda v: 255 - int((255 - v) * strength)))


for k in prompts:
    p = os.path.join(GEN, 'prologfin_s1_%s_0.jpg' % k)
    if not os.path.exists(p):
        continue
    im = Image.open(p).convert('RGB').resize((FW, FH), Image.LANCZOS)
    out = vignette(im).resize((OUTW, OUTH), Image.LANCZOS)
    dst = os.path.join(FIN, 's1_%s.png' % k)
    out.save(dst)
    print('final s1_%s -> %s' % (k, os.path.relpath(dst, HERE)))

# --- лист сравнения: было / a / b ---------------------------------------
now = os.path.join(FIN, 's1.png')
panels = []
if os.path.exists(now):
    panels.append((Image.open(now).convert('RGB'), 'БЫЛО · без рисунка мелом'))
for k, cap in (('a', 'A · мелом в кадре (впечено)'), ('b', 'B · мелом в кадре (впечено)')):
    p = os.path.join(FIN, 's1_%s.png' % k)
    if os.path.exists(p):
        panels.append((Image.open(p).convert('RGB'), cap))
if panels:
    pad, caph, hdr, gap = 20, 44, 82, 10
    cw = panels[0][0].width
    rh = round(panels[0][0].height * cw / panels[0][0].width)
    H = hdr + len(panels) * (rh + caph + gap) + pad
    c = Image.new('RGB', (cw + 2 * pad, H), (13, 14, 19)); d = ImageDraw.Draw(c)
    d.text((pad, 16), '«ЗАРЯНКА» · S1 — котобус мелом ВПЕЧЁН в кадр (flux-2) против «без рисунка»',
           font=ImageFont.truetype(LATO_B, 27), fill=(226, 186, 104))
    y = hdr
    for im, cap in panels:
        r = im.resize((cw, rh), Image.LANCZOS)
        c.paste(r, (pad, y)); d.rectangle([pad, y, pad + r.width, y + r.height], outline=(60, 62, 74))
        d.text((pad + 4, y + r.height + 7), cap, font=ImageFont.truetype(LATO_B, 22), fill=(240, 236, 228))
        y += rh + caph + gap
    c.save(os.path.join(REV, 'review_85_s1_baked.png'))
    print('sheet -> assets/review/review_85_s1_baked.png', c.size)
