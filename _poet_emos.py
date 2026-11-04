# -*- coding: utf-8 -*-
"""Эмоции ПОЭТА (Лёша Савушкин) — два вида по канону 2016 (`old:Sprites`):

  «Должен появляться в двух видах. С длинной плохой прической и аккуратно стриженный.»
  эмоции: с волосами — нормальный, заинтересованный, расстроенный;
          стриженный   — нормальный, утомлённый, одухотворённое.

База — принятый Иваном `poet2_b_0.png` (2026-11-04: «больше представляю как v2-B»).
Поза, ракурс, одежда и лицо держатся референсом, меняется ТОЛЬКО выражение лица
(и причёска у стриженного вида) — иначе эмоции не переключаются в движке.

  poet_ha_*   — с длинными волосами: neutral / interested / upset
  poet_sh_*   — стриженный, повзрослевший: neutral / tired / inspired

Стриженный вид: сначала генерится neutral (он же референс для двух других), потому что
волосы в кадре меняются целиком — иначе лицо «уплывёт».

Запуск:
    python3 _poet_emos.py --dry
    python3 _poet_emos.py                 # всё, ~2.70 ₽
    python3 _poet_emos.py poet_ha_upset   # точечно
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen  # noqa: E402
import pv  # noqa: E402

BASE = os.path.join(HERE, 'assets', 'gen', 'poet2_b_0.png')
def _first(*cands):
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[0]


SHORT_NEUTRAL = _first(os.path.join(HERE, 'assets', 'gen', 'poet_sh_neutral_0.png'),
                       os.path.join(HERE, 'assets', 'gen', 'poet_sh_neutral_0.jpg'))

LOCK = (
    "СОХРАНИ ТОЧНО того же персонажа, что на приложенном спрайте: то же лицо (округлое, "
    "мягкие щёки, округлый подбородок, короткий нос, обычные серые глаза — не аниме), "
    "та же лёгкая небритость на щеках и над губой, та же одежда (тёмная куртка поверх "
    "светлой рубашки), тот же ракурс чуть вполоборота, то же кадрирование поясного "
    "спрайта, тот же ровный однотонный светло-серый фон, та же манера рисования — мягкая "
    "живопись с видимыми мазками. Меняется ТОЛЬКО выражение лица. "
    "НЕ аниме, НЕ манга, НЕ galge, НЕ cel-shading, НЕ 3D, НЕ фото."
)

LONG_HAIR = "Волосы ТЁМНЫЕ, длинные и неухоженные, спадают на плечи неровными прядями."

SHORT_HAIR = (
    "Волосы КОРОТКО И АККУРАТНО ПОДСТРИЖЕНЫ (он последовал совету «И подстригитесь»), "
    "тёмные, аккуратная мужская стрижка средней длины, лицо открыто. Он же, но заметно "
    "повзрослевший и посвежевший: осанка ровнее, взгляд спокойнее."
)

EXPR = {
    'neutral':    "Выражение лица СПОКОЙНОЕ И НЕЙТРАЛЬНОЕ: губы сомкнуты, взгляд прямой.",
    'interested': ("Выражение ЗАИНТЕРЕСОВАННОЕ: брови чуть приподняты, глаза чуть шире, "
                   "голова слегка приподнята, на губах едва заметная живая полуулыбка."),
    'upset':      ("Выражение РАССТРОЕННОЕ И ПОТЕРЯННОЕ: брови сведены, уголки губ опущены, "
                   "глаза потухшие, голова опущена ниже, плечи поникли — человек, которому "
                   "только что отказали."),
    'tired':      ("Выражение УТОМЛЁННОЕ: веки чуть приспущены, тени под глазами, губы "
                   "сжаты, голова тяжело склонена, плечи устало опущены."),
    'inspired':   ("Выражение ОДУХОТВОРЁННОЕ: глаза горят, взгляд вверх-вдаль, губы "
                   "приоткрыты в лёгкой улыбке, голова поднята, спина выпрямлена — человек, "
                   "нашедший своё дело."),
}

JOBS = [
    ('poet_ha_neutral',    LONG_HAIR, 'neutral',    BASE),
    ('poet_ha_interested', LONG_HAIR, 'interested', BASE),
    ('poet_ha_upset',      LONG_HAIR, 'upset',      BASE),
    ('poet_sh_neutral',    SHORT_HAIR, 'neutral',    BASE),
    ('poet_sh_tired',      SHORT_HAIR, 'tired',      'SHORT'),
    ('poet_sh_inspired',   SHORT_HAIR, 'inspired',   'SHORT'),
]


def ref_for(src):
    if src == 'SHORT':
        return SHORT_NEUTRAL
    return src


def main(only=None, model="gpt-image-2"):
    dry = "--dry" in sys.argv
    for name, hair, expr, src in JOBS:
        if only and name not in only:
            continue
        ref = ref_for(src)
        if not os.path.exists(ref):
            print('[skip] %-18s нет референса %s' % (name, os.path.basename(ref)), flush=True)
            continue
        prompt = "%s %s\n\n%s" % (LOCK, hair, EXPR[expr])
        opts = {"aspect_ratio": "3:4", "resolution": "1K", "input_base64": [gen.b64(ref, max_w=1024)]}
        q = pv.price(model, prompt, opts)
        print('[quote] %-18s %s RUB (ref %s)' % (name, q.get('priceRub'),
                                                 os.path.basename(ref)), flush=True)
        if dry:
            continue
        try:
            files, st = pv.generate_to_files(model, prompt, opts, outdir="assets/gen",
                                             name=name, max_price_rub=12)
            print('[ok] %-18s %s' % (name, [os.path.basename(f) for f in files]), flush=True)
        except Exception as e:  # noqa: BLE001
            print('[fail] %-18s %s' % (name, str(e)[:160]), flush=True)


if __name__ == '__main__':
    only = [a for a in sys.argv[1:] if not a.startswith('-')]
    main(only or None)
