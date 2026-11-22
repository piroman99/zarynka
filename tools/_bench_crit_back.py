# -*- coding: utf-8 -*-
"""Критик пропа: с какой стороны стоек прибиты планки спинки."""
import base64
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

SRC = os.path.join(ROOT, '_sat', 'blend', os.environ.get('SRC', 'bench6_preview.jpg'))
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')

im = Image.open(SRC).convert('RGB')
im.thumbnail((1400, 1400), Image.LANCZOS)
out = os.path.join(ROOT, '_sat', 'blend', 'crit_backslats.jpg')
im.save(out, quality=92)
print('crit', os.path.relpath(out, HERE), im.size)

PROMPT = """3D-рендер простой садовой скамейки. Сиденье смотрит на зрителя (направо-вперёд),
спинка — дальше от зрителя.

Смотри ТОЛЬКО на планки спинки и стойки (задние ножки, которые держат спинку):

{
 "back_boards_side": "планки спинки прибиты С ВНУТРЕННЕЙ стороны (между стойками, со стороны сидящего) или СНАРУЖИ (за стойками, со стороны газона) или ВРОВЕНЬ со стойками",
 "how_you_see_it": "одна фраза, по какому признаку так решил",
 "boards_overlap_posts": "видно ли, что стойки выступают за плоскость планок или планки выступают за стойки",
 "slat_ends": "торцы планок спинки совпадают по длине или торчат с одной стороны",
 "still_weird": ["что ещё выглядит неправильно"]
}
Только JSON."""

with open(out, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')
body = {"model": MODEL, "temperature": 0.0, "messages": [{"role": "user", "content": [
    {"type": "text", "text": PROMPT},
    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
r, cost = pv._req("POST", "/v1/chat/completions", body, timeout=180)
print('cost', cost)
txt = r["choices"][0]["message"]["content"].strip()
i, j = txt.find('{'), txt.rfind('}')
print(txt[:1500])
if i >= 0 and j > i:
    try:
        print(json.dumps(json.loads(txt[i:j + 1]), ensure_ascii=False, indent=2))
    except Exception as e:
        print('json fail', e)
