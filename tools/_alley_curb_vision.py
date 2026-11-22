# -*- coding: utf-8 -*-
"""Где на фоне аллеи левый бордюр: замер моделью со зрением по сетке 0.05.

Мой собственный фит дал x = 0.2856*y - 108.5, но у него было всего 24 инлайера из 119 —
доверия мало. Спрашиваю точечно по нескольким строкам.
"""
import base64
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
OUT = os.path.join(ROOT, '_sat', 'curb_grid.jpg')

im = Image.open(BG).convert('RGB').resize((1600, 900), Image.LANCZOS)
W, H = im.size
d = ImageDraw.Draw(im)
for i in range(1, 20):
    x = W * i / 20.0
    d.line([(x, 0), (x, H)], fill=(255, 0, 200), width=2)
    d.text((x + 3, 6), '%.2f' % (i / 20.0), fill=(255, 0, 200))
for j in range(1, 20):
    y = H * j / 20.0
    d.line([(0, y), (W, y)], fill=(0, 200, 255), width=2)
    d.text((4, y + 1), '%.2f' % (j / 20.0), fill=(0, 120, 200))
im.save(OUT, quality=90)
print('grid', os.path.relpath(OUT, HERE), im.size)

PROMPT = """Акварельный кадр: весенняя аллея в парке, уходит в глубину. Розовые линии — доли
ширины кадра (0.00…0.95 через 0.05, подписаны сверху), голубые — доли высоты (подписаны слева).

Мне нужно понять, где КОНЧАЕТСЯ газон и НАЧИНАЕТСЯ асфальт по ЛЕВОЙ стороне аллеи
(то есть где левый бордюр/край покрытия) на нескольких высотах.

Ответь JSON, x — в долях ШИРИНЫ, y — в долях ВЫСОТЫ, по линиям сетки:
{
 "curb_left_x": {
   "y_0.60": ,
   "y_0.70": ,
   "y_0.80": ,
   "y_0.90": ,
   "y_0.95": 
 },
 "curb_visible": "да/нет, виден ли бордюр как каменный поребрик",
 "walkway_edges": {
   "left_at_y_0.90": ,
   "right_at_y_0.90": 
 },
 "frame_scale": "сколько метров в ширине аллеи на уровне y=0.90, если стоящий человек
                 ростом 1.70 м занимает по высоте около 0.57 кадра",
 "notes": "короткое пояснение по геометрии"
}
Только JSON."""

with open(OUT, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')
body = {"model": MODEL, "temperature": 0.0, "messages": [{"role": "user", "content": [
    {"type": "text", "text": PROMPT},
    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
r, cost = pv._req("POST", "/v1/chat/completions", body, timeout=180)
print('cost', cost)
txt = r["choices"][0]["message"]["content"].strip()
t = txt.split('```')[1] if txt.startswith('```') else txt
i, j = t.find('{'), t.rfind('}')
print(txt[:2000])
if i >= 0 and j > i:
    try:
        obj = json.loads(t[i:j + 1])
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        for k, v in (obj.get('curb_left_x') or {}).items():
            try:
                yy = float(k.split('_')[1])
                print('  бордюр при y=%.2f -> x=%.2f  (= %.0f px в 1920)' % (yy, float(v), float(v) * 1920))
            except Exception:  # noqa: BLE001
                pass
    except Exception as e:  # noqa: BLE001
        print('json fail', e)
