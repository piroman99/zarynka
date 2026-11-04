# -*- coding: utf-8 -*-
"""Подмножества шрифтов для ТИТР-СЛОЯ движка (vn2/fonts/*.woff2).

Зачем: надписи кадров пролога раньше вжигались в PNG шрифтами URWGothic-Demi и
Lato-Bold. С 2026-11-01 они уходят в титр-слой движка (pg.ovl) — значит браузеру
нужны ТЕ ЖЕ шрифты, иначе вид разъедется с тем, что Иван уже принял.

Кириллица в этих шрифтах есть, но целиком Lato-Bold = 657 КБ. Подмножество
(латиница + кириллица + пунктуация) в WOFF2 — десятки КБ.

Запуск: python3 _vn2_fonts.py   (нужны fonttools + brotli; лежат в ./_pylib)
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '_pylib'))

from fontTools import subset  # noqa: E402

OUT = os.path.join(HERE, 'vn2', 'fonts')
os.makedirs(OUT, exist_ok=True)

ASCII = ''.join(chr(c) for c in range(0x20, 0x7F))
RU = ('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
      'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
PUNCT = '«»—–…·.,!?:;()/\\№"\'‘’“”'
TEXT = ''.join(dict.fromkeys(ASCII + RU + PUNCT))

FONTS = [
    ('/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf', 'gothic-demi.woff2'),
    ('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 'lato-bold.woff2'),
]

for src, dst in FONTS:
    if not os.path.exists(src):
        raise SystemExit('нет исходного шрифта: %s' % src)
    out = os.path.join(OUT, dst)
    args = [src, '--text=%s' % TEXT, '--flavor=woff2', '--output-file=%s' % out,
            '--layout-features=kern,liga', '--no-hinting', '--desubroutinize',
            '--name-IDs=*', '--drop-tables+=DSIG']
    subset.main(args)
    print('%-16s %7d Б  (исходник %d Б)' % (dst, os.path.getsize(out), os.path.getsize(src)))
print('готово ->', os.path.relpath(OUT, HERE))
