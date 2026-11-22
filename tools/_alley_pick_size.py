# -*- coding: utf-8 -*-
"""Какой из трёх размеров поэта выглядит правильно (модель со зрением)."""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

IMG = os.path.join(ROOT, '_sat', os.environ.get('SRC', 'v9_sheet.jpg'))
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')

PROMPT = """Три варианта одного кадра (A слева, B в центре, C справа): акварельная парковая
аллея, деревянная скамейка и сидящий на ней человек — вставлен программно. Скамейка во всех
трёх вариантах одинаковая и правильная. Отличается ТОЛЬКО размер сидящего человека.

Ответь JSON:
{
 "sits_on_bench": {"A": "да/нет, таз на доске или висит", "B": ..., "C": ...},
 "size_correct": {"A": "мелкий/нормальный/крупный", "B": ..., "C": ...},
 "best": "A | B | C",
 "what_wrong_with_best": "одной фразой остаток проблемы, если есть",
 "is_hanging": {"A": "да/нет", "B": ..., "C": ...}
}
Только JSON."""

with open(IMG, 'rb') as f:
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
