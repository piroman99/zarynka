# -*- coding: utf-8 -*-
"""Критика v5 моделью со зрением: висит ли поэт, стоит ли задняя ножка у бордюра."""
import base64
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

SRC = os.path.join(ROOT, '_sat', os.environ.get('SRC', 'alley_prev5.jpg'))
GRID = SRC.replace('.jpg', '_grid.jpg')
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')

im = Image.open(SRC).convert('RGB')
W, H = im.size
d = ImageDraw.Draw(im)
for i in range(1, 10):
    d.line([(W * i / 10, 0), (W * i / 10, H)], fill=(255, 50, 50), width=3)
    d.line([(0, H * i / 10), (W, H * i / 10)], fill=(255, 50, 50), width=3)
for i in range(10):
    d.text((W * i / 10 + 8, 8), '%.1f' % (i / 10), fill=(220, 0, 0))
    d.text((8, H * i / 10 + 6), '%.1f' % (i / 10), fill=(220, 0, 0))
im.save(GRID, quality=88)
print('grid:', os.path.relpath(GRID, HERE))

PROMPT = """Кадр визуальной новеллы (акварельный фон — парковая аллея; поверх вставлены
деревянная скамейка и человек). Красная сетка: доли кадра (0.0 слева/сверху).

Вопросы строго по делу, отвечай JSON:
{
 "bench_legs": {
   "back_left_leg_xy": [x, y] точки, где задняя левая ножка (та, что ближе к левому краю
                        и сзади) касается земли,
   "is_leg_near_curb": "да/нет — стоит ли эта ножка вплотную к бордюру",
   "on_asphalt_or_grass": "ножка на асфальте | на бордюре | на газоне"
 },
 "bench_geometry": {
   "along_path": "ось скамейки вдоль края аллеи или поперёк",
   "seat_y_at_poet": "y (доля кадра) плоскости сиденья прямо под сидящим",
   "bench_len_px_pct": "длина скамейки в % ширины кадра"
 },
 "poet": {
   "is_floating": "да/нет — таз человека висит в воздухе над сиденьем",
   "seat_contact_y": "y (доля кадра) точки, где таз касается сиденья",
   "gap_px_fraction": "зазор между тазом и сиденьем в долях ВЫСОТЫ кадра (0 = касается)",
   "size_vs_bench": "человек крупнее/мельче, чем должен быть для этой скамейки",
   "feet_touch": "ступни на земле | висят | утоплены в землю"
 },
 "verdict": "одной фразой: что главное поправить"
}
Только JSON."""

with open(GRID, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')
body = {"model": MODEL, "temperature": 0.0, "messages": [{"role": "user", "content": [
    {"type": "text", "text": PROMPT},
    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
r, cost = pv._req("POST", "/v1/chat/completions", body, timeout=180)
print('cost', cost)
txt = r["choices"][0]["message"]["content"].strip()
t = txt.split('```')[1] if txt.startswith('```') else txt
i, j = t.find('{'), t.rfind('}')
print(txt[:2500])
if i >= 0 and j > i:
    try:
        print(json.dumps(json.loads(t[i:j + 1]), ensure_ascii=False, indent=2))
    except Exception as e:  # noqa: BLE001
        print('json fail', e)
