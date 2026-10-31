# -*- coding: utf-8 -*-
"""Кадр p8 принят (вариант B, с остеклением) -> в движок; старый S2 (цех) уходит в архив.

Что делает:
  1) assets/final/prolog/p8.png      <- prolog_p8v4_b__gpt-image-2_0.png (мастер, без грейда)
  2) assets/final/prolog/s2.png      -> assets/rejected/s2/s2_ceh_prologfin2.png (архив,
     по правилу «отклонённые кадры не удаляем»; запись в assets/rejected/REJECTED.md)
  3) vn2/audio/vo/s2_00.mp3          -> p8_00.mp3 (текст тот же, переозвучка не нужна)
  4) _vn2_build.py: узел s2 -> p8 (текст «Космонавты начали тренировки…» переезжает на кадр
     гидролаборатории; кадр цеха теперь один — p7, дубль убираем)
  5) PROLOG_IDS/списки в проверках обновляются отдельно (_voices_sync_prolog.py и др.)

Запуск: python3 _p8_adopt.py
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
FIN = os.path.join(HERE, "assets", "final", "prolog")
REJ = os.path.join(HERE, "assets", "rejected", "s2")
VO = os.path.join(HERE, "vn2", "audio", "vo")
MAN = os.path.join(VO, "_voices.json")

os.makedirs(REJ, exist_ok=True)

src = os.path.join(GEN, "prolog_p8v4_b__gpt-image-2_0.png")
dst = os.path.join(FIN, "p8.png")
shutil.copyfile(src, dst)
print("мастер p8.png <-", os.path.relpath(src, HERE), os.path.getsize(dst), "B")

old_s2 = os.path.join(FIN, "s2.png")
if os.path.exists(old_s2):
    tgt = os.path.join(REJ, "s2_ceh_prologfin2.png")
    shutil.move(old_s2, tgt)
    print("архив s2.png ->", os.path.relpath(tgt, HERE), os.path.getsize(tgt), "B")

# озвучка: тот же самый текст, просто новое имя файла
old_mp3 = os.path.join(VO, "s2_00.mp3")
new_mp3 = os.path.join(VO, "p8_00.mp3")
if os.path.exists(old_mp3):
    shutil.move(old_mp3, new_mp3)
    print("озвучка s2_00.mp3 ->", os.path.basename(new_mp3), os.path.getsize(new_mp3), "B")

import json
man = json.load(open(MAN, encoding="utf-8"))
if "audio/vo/s2_00.mp3" in man:
    man["audio/vo/p8_00.mp3"] = man.pop("audio/vo/s2_00.mp3")
    json.dump(man, open(MAN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("манифест: s2_00 -> p8_00")
else:
    print("манифест: записи s2_00 нет (проверить)")

note = ("- `s2/s2_ceh_prologfin2.png` — S2 «цех сборки» (prologfin2_s2a): кадр цеха стал "
        "дублем нового p7 из плотной сетки, поэтому его заменил кадр p8 «гидролаборатория» "
        "(тот же текст «Космонавты начали тренировки…») _(2026-10-31)_\n")
p = os.path.join(HERE, "assets", "rejected", "REJECTED.md")
txt = open(p, encoding="utf-8").read()
if "s2_ceh_prologfin2" not in txt:
    if not txt.endswith("\n"):
        txt += "\n"
    open(p, "w", encoding="utf-8").write(txt + note)
    print("REJECTED.md дополнен")