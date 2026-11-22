# -*- coding: utf-8 -*-
"""Спросить у chat-модели со зрением про геометрию фона аллеи (своих глаз у меня нет).

Вопросы: где тротуар/бордюр, куда уходит аллея, где логичное место скамейки ВДОЛЬ
тротуара и под каким углом её ставить. Модель просят вернуть JSON с координатами
в долях кадра — чтобы не гадать по словам.
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pv  # noqa: E402

IMG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
MODEL = os.environ.get('VISION_MODEL', 'google/gemini-3.8-flash')

PROMPT = """Ты помогаешь расставить мебель в нарисованном кадре (акварель, весенняя аллея
в парке, 16:9). Нужна ТОЛЬКО геометрия. Смотри внимательно и ответь JSON-объектом:

{
  "path": {
    "what": "что именно в кадре является пешеходной дорожкой/аллеей",
    "left_edge_x_at_bottom": 0.0-1.0,
    "left_edge_x_at_horizon": 0.0-1.0,
    "right_edge_x_at_bottom": 0.0-1.0,
    "right_edge_x_at_horizon": 0.0-1.0,
    "horizon_y": 0.0-1.0,
    "curb": "есть ли бордюр/поребрик, с какой стороны"
  },
  "bench": {
    "where_should_it_stand": "вдоль какой стороны дорожки, у бордюра или на газоне",
    "anchor_x": 0.0-1.0,
    "anchor_y_ground": 0.0-1.0,
    "length_px_pct_of_width": сколько процентов ШИРИНЫ кадра займёт скамейка длиной 1.8 м,
    "tilt_deg": насколько скамейка должна быть наклонена (в градусах, 0 = строго горизонтально,
                 плюс = дальний конец выше/правее),
    "why": "короткое объяснение"
  },
  "notes": "что ещё важно для вставки скамейки в этот кадр (перекрытия, тени, цвет)"
}

Координаты — доли кадра: x=0 левый край, x=1 правый, y=0 верх, y=1 низ.
Отвечай только JSON, без пояснений вокруг."""


def main():
    with open(IMG, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    body = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}},
            ],
        }],
        "temperature": 0.2,
    }
    print('model:', MODEL, 'image bytes:', os.path.getsize(IMG), flush=True)
    d, cost = pv._req("POST", "/v1/chat/completions", body, timeout=180)
    print('cost_header:', cost, flush=True)
    txt = d["choices"][0]["message"]["content"]
    print('--- raw ---')
    print(txt[:4000])
    # вытащить JSON, если он в ```-блоке
    t = txt.strip()
    if t.startswith('```'):
        t = t.split('```')[1]
        t = t[t.find('{'):]
    i, j = t.find('{'), t.rfind('}')
    if i >= 0 and j > i:
        try:
            obj = json.loads(t[i:j + 1])
            print('--- json ---')
            print(json.dumps(obj, ensure_ascii=False, indent=2))
        except Exception as e:  # noqa: BLE001
            print('json parse fail:', e)


if __name__ == '__main__':
    main()
