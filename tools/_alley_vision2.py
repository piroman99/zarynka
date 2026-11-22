# -*- coding: utf-8 -*-
"""Критика вставки скамейки моделью со зрением (своих глаз у меня нет).

Берёт `_sat/alley_prev3.jpg`, рисует поверх сетку 10x10 с подписями координат
(доли кадра), и просит модель ответить строго по пунктам: вдоль или поперёк дороги,
на газоне или на дороге, правилен ли размер, где именно сдвинуть.
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

SRC = os.path.join(ROOT, '_sat', 'alley_prev3.jpg')
GRID = os.path.join(ROOT, '_sat', 'alley_prev3_grid.jpg')
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')

im = Image.open(SRC).convert('RGB')
W, H = im.size
d = ImageDraw.Draw(im)
for i in range(1, 10):
    x, y = W * i / 10.0, H * i / 10.0
    d.line([(x, 0), (x, H)], fill=(255, 60, 60), width=3)
    d.line([(0, y), (W, y)], fill=(255, 60, 60), width=3)
for i in range(10):
    d.text((W * i / 10.0 + 8, 10), '%.1f' % (i / 10.0), fill=(255, 0, 0))
    d.text((10, H * i / 10.0 + 6), '%.1f' % (i / 10.0), fill=(255, 0, 0))
im.save(GRID, quality=88)
print('grid:', os.path.relpath(GRID, HERE), im.size)

PROMPT = """Это кадр визуальной новеллы (акварель, парковая аллея). Поверх нанесена
красная сетка: подписи — доли кадра (0.0 слева/сверху, 1.0 справа/снизу).

В кадр вставлена деревянная скамейка (и на ней сидит человек в тёмной куртке, справа
стоит женщина в синем комбинезоне). Вставка сделана программно, надо её проверить.

Ответь строго JSON:
{
 "alley_direction": "куда уходит аллея (в каком направлении от камеры) и под каким углом
                      к горизонтали идёт её левый край",
 "bench_orientation": {
   "along_or_across": "вдоль дороги или поперёк",
   "angle_vs_path_deg": насколько ось скамейки отклоняется от направления дороги, градусы,
   "verdict": "ok | повернуть на N градусов по часовой | против часовой"
 },
 "bench_placement": {
   "on_path_or_grass": "на асфальте или на газоне",
   "distance_from_curb": "у самого бордюра / в метре от него / далеко",
   "shift_needed": "сдвинуть влево/вправо/вверх/вниз на сколько долей кадра"
 },
 "bench_scale": {
   "verdict": "маленькая | нормальная | большая",
   "why": "сравни со стоящей женщиной (её рост 1.70 м) и с шириной дороги"
 },
 "person_fit": {
   "verdict": "человек сидит правильно | висит над скамейкой | провалился в неё",
   "how_off": "на сколько пикселей или сантиметров промах"
 },
 "other_problems": ["список того, что ещё не так, коротко"]
}
Отвечай ТОЛЬКО JSON."""

with open(GRID, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')
body = {
    "model": MODEL,
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": PROMPT},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}},
    ]}],
    "temperature": 0.1,
}
d2, cost = pv._req("POST", "/v1/chat/completions", body, timeout=180)
print('cost_header:', cost)
txt = d2["choices"][0]["message"]["content"].strip()
print('--- raw ---\n', txt[:3500])
t = txt
if t.startswith('```'):
    t = t.split('```')[1]
i, j = t.find('{'), t.rfind('}')
if i >= 0 and j > i:
    try:
        obj = json.loads(t[i:j + 1])
        print('--- json ---')
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    except Exception as e:  # noqa: BLE001
        print('json fail:', e)
