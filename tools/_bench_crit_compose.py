# -*- coding: utf-8 -*-
"""Критик вставки: скамейка простой формы + поэт в кадре «аллея»."""
import base64
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

SRC = os.path.join(ROOT, '_sat', os.environ.get('SRC', 'blend_bench_crop.jpg'))
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')

im = Image.open(SRC).convert('RGB')
im.thumbnail((1400, 1400), Image.LANCZOS)
out = os.path.join(ROOT, '_sat', 'blend', 'crit_compose.jpg')
im.save(out, quality=92)
print('crit', os.path.relpath(out, HERE), im.size)

PROMPT = """Кроп кадра визуальной новеллы: акварельная парковая аллея, на переднем плане
программно вставленная 3D-скамейка, на ней сидит человек спиной/вполоборота.

{
 "bench_shape": "опиши форму скамейки в двух словах",
 "armrests": "есть ли подлокотники или боковые щиты — да/нет",
 "looks_odd": ["что выглядит странно: пропорции, посадка, ножки, стык с землёй"],
 "poet_seated": "сидит на доске / висит / провалился",
 "poet_scale": "пропорционален скамейке или нет",
 "bench_float": "стоит на земле или парит",
 "style_mismatch": "насколько выбивается из акварельного фона: сильно/средне/слегка",
 "improve": ["2 пункта, что поправить в первую очередь"]
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
print(txt[:1600])
if i >= 0 and j > i:
    try:
        print(json.dumps(json.loads(txt[i:j + 1]), ensure_ascii=False, indent=2))
    except Exception as e:
        print('json fail', e)
