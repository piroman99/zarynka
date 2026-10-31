# -*- coding: utf-8 -*-
"""p8: замена принятого кадра B (два ряда иллюминаторов) на A (один ряд).

Иван 2026-11-01: «Не, мне нравится вариант с одним рядом иллюминаторов.
Как то ламповее и теплее выглядит».

Мастер B остаётся в assets/gen (не удаляем), просто меняем финальный кадр.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
FIN = os.path.join(HERE, "assets", "final", "prolog")

src = os.path.join(GEN, "prolog_p8v4_a__gpt-image-2_0.png")
dst = os.path.join(FIN, "p8.png")

bak = os.path.join(FIN, "p8_v4b_bak.png")
if os.path.exists(dst) and not os.path.exists(bak):
    shutil.copyfile(dst, bak)
    print("бэкап прежнего B:", os.path.relpath(bak, HERE), os.path.getsize(bak), "B")

shutil.copyfile(src, dst)
print("p8.png <-", os.path.relpath(src, HERE), os.path.getsize(dst), "B")

from PIL import Image
im = Image.open(dst)
print("размер:", im.size, im.mode)
