# -*- coding: utf-8 -*-
"""Убрать осиротевшую озвучку старого узла s5 (текст разрезан на s5a + s5b)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(HERE, 'vn2', 'audio', 'vo')
MAN = os.path.join(VO, '_voices.json')

man = json.load(open(MAN, encoding='utf-8'))
for key in list(man):
    if os.path.basename(key) in ('s5_00.mp3', 's5_01.mp3'):
        del man[key]
        print('манифест: убрал', key)
json.dump(man, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('записей в манифесте:', len(man))

for f in ('s5_00.mp3', 's5_01.mp3'):
    p = os.path.join(VO, f)
    if os.path.exists(p):
        os.remove(p)
        print('удалён', f)
print('готово')
