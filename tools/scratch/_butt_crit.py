# -*- coding: utf-8 -*-
"""Один бинарный вопрос по крупному кропу: есть ли щель между телом и доской."""
import base64
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import pv  # noqa: E402

SRC = os.path.join(ROOT, '_sat', os.environ.get('SRC', 'FINAL50_butt.jpg'))
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')

im = Image.open(SRC).convert('RGB')
im.thumbnail((1300, 1300), Image.LANCZOS)
out = os.path.join(ROOT, '_sat', 'butt_crit.jpg')
im.save(out, quality=94)
print('crit', os.path.relpath(out, HERE), im.size)

PROMPT = """Крупный кроп: деревянная садовая скамейка, на ней сидит человек в три четверти.

{
 "person_touches_seat": "да/нет — соприкасается ли тело человека с доской сиденья",
 "gap_under_person": "да/нет — виден ли ПОЗАДИ человека, под его задней частью, просвет или фон вместо доски",
 "seat_visible_under_butt": "видна ли доска прямо под сидящим человеком",
 "person_sunk_too_deep": "человек провалился в скамейку / сидит нормально / висит над ней",
 "feet_position": "ступни на земле / выше земли / ниже земли",
 "one_line": "одна фраза: что не так с посадкой, если что-то не так"
}
Только JSON."""

with open(out, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')
body = {"model": MODEL, "temperature": 0.0, "messages": [{"role": "user", "content": [
    {"type": "text", "text": PROMPT},
    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
r, cost = pv._req("POST", "/v1/chat/completions", body, timeout=180)
txt = r["choices"][0]["message"]["content"].strip()
i, j = txt.find('{'), txt.rfind('}')
print(json.dumps(json.loads(txt[i:j + 1]), ensure_ascii=False, indent=2) if i >= 0 else txt)
