# -*- coding: utf-8 -*-
"""Кадр p6 делится ПОПОЛАМ (Иван 2026-11-04):

  стр. 1 «Вторая Марсианская… Один раз были?»  -> старый кадр С МАРСА (вернуть);
  стр. 2 «…лучше лунную базу до ума доведите»  -> ЛУННАЯ станция (p6luna_b).

Что делает:
  1) возвращает марсианский мастер из архива: assets/rejected/p6/p6_mars_B_mid_dust.png
     -> assets/final/prolog/p6.png;
  2) кладёт мастером лунной станции assets/final/prolog/p6luna.png (без грейда и без
     метки — грейд и ресайз делает `_vn2_build.py`, как у остальных вставленных кадров);
  3) пишет `PAGE_BG` для стр. 2 узла p6 в `_vn2_build.py` (правим строкой, не руками).

Запуск: python3 _p6_split.py [--dry]
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')
GEN = os.path.join(HERE, 'assets', 'gen')
REJ = os.path.join(HERE, 'assets', 'rejected', 'p6')
MD = os.path.join(HERE, 'assets', 'rejected', 'REJECTED.md')

MARS = os.path.join(REJ, 'p6_mars_B_mid_dust.png')
LUNA = os.path.join(GEN, 'p6luna_b__gpt-image-2_0.png')

for p in (MARS, LUNA):
    if not os.path.exists(p):
        raise SystemExit('нет файла %s' % p)

if '--dry' in sys.argv:
    raise SystemExit(0)

shutil.copy2(MARS, os.path.join(FIN, 'p6.png'))
print('p6.png <- Марс (из архива) %d B' % os.path.getsize(os.path.join(FIN, 'p6.png')))
shutil.copy2(LUNA, os.path.join(FIN, 'p6luna.png'))
print('p6luna.png <- p6luna_b %d B' % os.path.getsize(os.path.join(FIN, 'p6luna.png')))

# REJECTED.md: марсианский мастер больше НЕ отклонён — он снова в сборке (стр. 1)
txt = open(MD, encoding='utf-8').read()
keep = []
for ln in txt.split('\n'):
    if 'p6_mars_B_mid_dust.png' in ln and 'лунная станция' in ln:
        keep.append('- `p6/p6_mars_B_mid_dust.png` — **вернулся в сборку** 2026-11-04: Иван '
                    'разделил кадр p6 пополам, стр. 1 «Вторая Марсианская… Один раз были?» '
                    'идёт под старый кадр С МАРСА, лунная станция — на стр. 2 '
                    '_(2026-11-04)_')
        continue
    keep.append(ln)
new = '\n'.join(keep)
if new != txt:
    open(MD, 'w', encoding='utf-8').write(new)
    print('REJECTED.md: строка про марсианский мастер обновлена')

BUILD = os.path.join(HERE, '_vn2_build.py')
src = open(BUILD, encoding='utf-8').read()
old = "PAGE_BG = {('s1', 0): 'img/prolog/s1a'}      # стр. 1 — стена с граффити, стр. 2 — подворотня"
new_line = ("PAGE_BG = {('s1', 0): 'img/prolog/s1a',   # s1: стр. 1 — стена с граффити, стр. 2 — подворотня\n"
            "           ('p6', 1): 'img/prolog/p6luna'}  # p6: стр. 1 — кадр С МАРСА, стр. 2 — лунная база")
if old in src:
    src = src.replace(old, new_line)
    open(BUILD, 'w', encoding='utf-8').write(src)
    print('_vn2_build.py: PAGE_BG += p6 стр.2 -> p6luna')
elif "('p6', 1)" in src:
    print('_vn2_build.py: PAGE_BG уже содержит p6')
else:
    raise SystemExit('не нашёл строку PAGE_BG — правь вручную')
