# -*- coding: utf-8 -*-
"""Критик для блендер-рендера скамейки: простота и правильность конструкции."""
import base64
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

SRC = os.path.join(ROOT, '_sat', 'blend', os.environ.get('SRC', 'bench2.png'))
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')

im = Image.open(SRC).convert('RGBA')
bg = Image.new('RGB', im.size, (246, 246, 244))
bg.paste(im, mask=im.split()[3])
bg.thumbnail((1400, 1400), Image.LANCZOS)
out = os.path.join(ROOT, '_sat', 'blend', 'crit_bench.jpg')
bg.save(out, quality=92)
print('crit', os.path.relpath(out, HERE), bg.size)

PROMPT = """Это 3D-рендер простой садовой скамейки (её потом вставят в акварельный кадр).
Описывай только то, что видно.

{
 "what_objects": "перечисли, что видно (планки сиденья, планки спинки, ножки, перекладины)",
 "armrests_or_side_panels": "есть ли подлокотники или боковые панели/щитки по бокам — да/нет",
 "legs_count_visible": 0-4,
 "legs_vertical": "ножки вертикальны или наклонены",
 "seat_and_back_parallel": "планки сиденья и спинки идут параллельно или разъезжаются",
 "shape_problems": ["короткий список: что выглядит криво/непонятно/лишнее"],
 "too_complex": "выглядит простой или перегруженной деталями",
 "reads_as_bench": "читается как обычная садовая скамейка — да/нет"
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
