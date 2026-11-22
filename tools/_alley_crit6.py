# -*- coding: utf-8 -*-
"""Критика v6 по КРОПУ вокруг скамейки (крупнее — точнее ответ)."""
import base64
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

SRC = os.path.join(ROOT, '_sat', os.environ.get('SRC', 'alley_prev6_full.jpg'))
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')
CROP = (0, int(1080 * 0.42), int(1920 * 0.58), 1080)

im = Image.open(SRC).convert('RGB')
c = im.crop(CROP)
c = c.resize((int(c.width * 1.6), int(c.height * 1.6)), Image.LANCZOS)
W, H = c.size
d = ImageDraw.Draw(c)
for i in range(1, 10):
    d.line([(W * i / 10, 0), (W * i / 10, H)], fill=(255, 0, 200), width=2)
    d.line([(0, H * i / 10), (W, H * i / 10)], fill=(0, 200, 255), width=2)
for i in range(10):
    d.text((W * i / 10 + 4, 4), '%.1f' % (i / 10), fill=(255, 0, 200))
    d.text((4, H * i / 10 + 3), '%.1f' % (i / 10), fill=(0, 140, 200))
out = os.path.join(ROOT, '_sat', 'crit6.jpg')
c.save(out, quality=90)
print('crit ->', os.path.relpath(out, HERE), c.size)

PROMPT = """Крупный кроп кадра визуальной новеллы: акварельный фон (парковая аллея) и
программно вставленная деревянная скамейка, на которой сидит человек (тёмная куртка,
руки у лица). Сетка: доли КРОПА.

Ответь строго JSON:
{
 "poet_seated_correctly": "да/нет",
 "butt_vs_seat": "таз касается доски сиденья | таз висит выше на X | таз провалился в скамейку",
 "gap_px": "зазор в пикселях этого кропа (0 если касается)",
 "feet": "ступни на земле | висят в воздухе на X | утоплены в землю",
 "poet_size": "мелкий/нормальный/крупный для этой скамейки (скамейка обычная, 1.8 м)",
 "bench_legs_on_ground": "да/нет, все ножки стоят на земле",
 "bench_vs_curb": "стоит ли скамейка на асфальте вдоль края/бордюра или поперёк дороги",
 "top_problem": "одной фразой: что главное поправить"
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
print(txt[:1500])
if i >= 0 and j > i:
    try:
        print(json.dumps(json.loads(t[i:j + 1]), ensure_ascii=False, indent=2))
    except Exception as e:  # noqa: BLE001
        print('json fail', e)
