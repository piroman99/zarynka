# -*- coding: utf-8 -*-
"""Критик для v10: цела ли скамейка справа, есть ли правая передняя ножка, не висит ли поэт."""
import base64
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

SRC = os.path.join(ROOT, '_sat', os.environ.get('SRC', 'alley_prev10_full.jpg'))
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')
im = Image.open(SRC).convert('RGB')
c = im.crop((0, int(1080 * 0.34), int(1920 * 0.62), 1080))
c = c.resize((int(c.width * 1.5), int(c.height * 1.5)), Image.LANCZOS)
W, H = c.size
d = ImageDraw.Draw(c)
for i in range(1, 10):
    d.line([(W * i / 10, 0), (W * i / 10, H)], fill=(255, 0, 200), width=2)
    d.line([(0, H * i / 10), (W, H * i / 10)], fill=(0, 200, 255), width=2)
    d.text((W * i / 10 + 4, 4), '%.1f' % (i / 10), fill=(255, 0, 200))
    d.text((4, H * i / 10 + 3), '%.1f' % (i / 10), fill=(0, 140, 200))
out = os.path.join(ROOT, '_sat', 'crit10.jpg')
c.save(out, quality=90)
print('crit', os.path.relpath(out, HERE), c.size)

PROMPT = """Крупный кроп кадра визуальной новеллы: акварельная парковая аллея, программно
вставленная деревянная скамейка со спинкой, на ней сидит человек. Сетка: доли КРОПА.

Проверь скамейку как предмет:
{
 "bench_complete": "да/нет — прорисована ли скамейка ЦЕЛИКОМ до дальнего (правого) конца,
                    или он тает/растворяется",
 "right_front_leg": "видна ли ПРАВАЯ ПЕРЕДНЯЯ ножка (у дальнего торца, со стороны зрителя):
                      да/нет, где она в долях",
 "how_many_legs_visible": 0-4,
 "far_end_quality": "плотный рисунок | полупрозрачный | обрыв",
 "bench_sits_on_ground": "да/нет — стоят ли ножки на асфальте, нет ли парящей доски",
 "poet_seated": "таз на доске | висит | провалился",
 "problems": ["короткий список остатка"]
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
t = txt.split('```')[1] if txt.startswith('```') else txt
i, j = t.find('{'), t.rfind('}')
print(txt[:1800])
if i >= 0 and j > i:
    try:
        print(json.dumps(json.loads(t[i:j + 1]), ensure_ascii=False, indent=2))
    except Exception as e:  # noqa: BLE001
        print('json fail', e)
