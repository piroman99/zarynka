# -*- coding: utf-8 -*-
"""Синхронизировать манифест озвучки пролога с собранным content.js.

После вставки кадра p6 текст абзаца L[7] разделён на две сцены (p6 + s2),
у s2 стало меньше страниц — манифест `vn2/audio/vo/_voices.json` остался от
прежней разбивки (s2_00 со старым текстом, s2_01/s2_02 без файлов, p6 нет вовсе).

Скрипт:
  * читает vn2/content.js, берёт узлы пролога (s1..s7 + p6);
  * для каждой страницы, у которой есть mp3, пишет запись {voice: narr, model, chars, price, text};
  * удаляет записи пролога, чьих mp3 больше нет;
  * приёмную (rec_*) не трогает.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(HERE, "vn2", "audio", "vo")
MAN = os.path.join(VO, "_voices.json")
PROLOG_IDS = {"s1", "p6", "s2", "s3", "s4", "s5", "s6", "s7"}
MODEL = "gemini-3.8-flash-tts"
PRICE_PER_1000 = 1.70

src = open(os.path.join(HERE, "vn2", "content.js"), encoding="utf-8").read()
# content.js = "window.VN = {...};" — вырезаем сам объект
body = src[src.index("{"): src.rindex("}") + 1]
data = json.loads(body)["nodes"]

man = json.load(open(MAN, encoding="utf-8"))
before = len(man)

added, updated, dropped = [], [], []
for node in data:
    if node.get("t") != "scene" or node.get("id") not in PROLOG_IDS:
        continue
    for pg in node.get("pages", []):
        rel = pg.get("vo")
        if not rel:
            continue
        path = os.path.join(HERE, "vn2", rel)
        key = rel
        rec = {"voice": "narr", "model": MODEL,
               "chars": len(pg["tx"]),
               "price": round(len(pg["tx"]) * PRICE_PER_1000 / 1000, 2),
               "text": pg["tx"]}
        if not os.path.exists(path):
            print("!! нет файла:", rel)
            continue
        if key in man:
            if man[key].get("text") != pg["tx"]:
                man[key] = rec
                updated.append(rel)
        else:
            man[key] = rec
            added.append(rel)

for key in list(man):
    base = os.path.basename(key)
    if base.split("_")[0] in PROLOG_IDS and not os.path.exists(os.path.join(HERE, "vn2", key)):
        del man[key]
        dropped.append(key)

json.dump(man, open(MAN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("записей в манифесте: %d -> %d" % (before, len(man)))
print("добавлено:", added)
print("обновлено:", updated)
print("удалено (файлов нет):", dropped)
