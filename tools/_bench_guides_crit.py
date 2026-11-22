# -*- coding: utf-8 -*-
"""Проверка по нарисованным линиям: отвечает ДА/НЕТ, а не «на глаз».

На кадр нанесены: малиновая — верхняя плоскость доски, голубая — земля.
Вопрос бинарный, чтобы ответ нельзя было «размазать».
"""
import base64
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

SRC = os.path.join(ROOT, '_sat', os.environ.get('SRC', 'final_guides_full.jpg'))
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')

im = Image.open(SRC).convert('RGB').crop((140, 260, 900, 1040))
im = im.resize((int(im.width * 1.6), int(im.height * 1.6)), Image.LANCZOS)
out = os.path.join(ROOT, '_sat', 'guides_crit.jpg')
im.save(out, quality=92)
print('crit', os.path.relpath(out, HERE), im.size)

PROMPT = """На картинке кадр визуальной новеллы. Поверх нарисованы две линии:
МАЛИНОВАЯ — верхняя плоскость доски сиденья скамейки;
ГОЛУБАЯ — линия земли под скамейкой;
ОРАНЖЕВАЯ (если есть) — предполагаемая линия таза сидящего человека.

Отвечай строго фактами о том, где линии проходят относительно человека и скамейки.

{
 "magenta_on_seat_top": "да/нет — малиновая линия идёт ровно по верхней кромке доски",
 "cyan_on_ground": "да/нет — голубая линия идёт по земле у нижних концов ножек",
 "where_is_person_bottom": "ниже, на, или выше малиновой линии находится НИЗ человека",
 "gap_between_person_and_seat": "виден ли просвет (прозрачное место) между телом человека и малиновой линией: да/нет",
 "feet_vs_cyan": "ступни человека выше / на / ниже голубой линии",
 "verdict": "человек сидит НА доске / парит над доской / провалился ниже доски"
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
print(txt[:1400])
if i >= 0 and j > i:
    print(json.dumps(json.loads(txt[i:j + 1]), ensure_ascii=False, indent=2))
