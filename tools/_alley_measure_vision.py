# -*- coding: utf-8 -*-
"""Замер деталей через модель со зрением: где у ПРОПА ножки и сиденье, где у ПОЭТА
линия «таз на сиденье» и ступни.

Своих глаз у меня нет, а без этих чисел поэт «висит». Обе картинки отдаются с сеткой
10x10 и подписями долей — чтобы ответ был в координатах, а не словами.
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
OUT = os.path.join(ROOT, '_sat')


def grid(path, out, bg=(240, 240, 240)):
    im = Image.open(path).convert('RGBA')
    canvas = Image.new('RGBA', im.size, bg + (255,))
    canvas.alpha_composite(im)
    im = canvas.convert('RGB')
    W, H = im.size
    d = ImageDraw.Draw(im)
    for i in range(1, 10):
        d.line([(W * i / 10, 0), (W * i / 10, H)], fill=(255, 40, 40), width=2)
        d.line([(0, H * i / 10), (W, H * i / 10)], fill=(255, 40, 40), width=2)
    for i in range(10):
        d.text((W * i / 10 + 4, 4), '%.1f' % (i / 10), fill=(200, 0, 0))
        d.text((4, H * i / 10 + 3), '%.1f' % (i / 10), fill=(200, 0, 0))
    im.save(out, quality=90)
    print('grid ->', os.path.relpath(out, HERE), im.size)
    return out


def ask(img, prompt):
    with open(img, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    body = {"model": MODEL, "temperature": 0.0, "messages": [{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
    d, cost = pv._req("POST", "/v1/chat/completions", body, timeout=180)
    txt = d["choices"][0]["message"]["content"].strip()
    print('cost', cost)
    t = txt
    if t.startswith('```'):
        t = t.split('```')[1]
    i, j = t.find('{'), t.rfind('}')
    if i < 0:
        print(t[:1500])
        return None
    try:
        return json.loads(t[i:j + 1])
    except Exception as e:  # noqa: BLE001
        print('json fail', e, t[:800])
        return None


PROP_Q = """На картинке — деревянная парковая скамейка со спинкой, нарисованная в перспективе
(она уходит в глубину вправо-вверх). Сетка: доли кадра, 0.0 слева/сверху.

Ответь JSON, все координаты — доли кадра (x, y):
{
 "seat_surface_line": {"x_near":, "y_near":, "x_far":, "y_far":},
 "backrest_top_line": {"x_near":, "y_near":, "x_far":, "y_far":},
 "legs": {
   "near_left":    {"x":, "y_bottom":, "where": "передняя левая / задняя левая ..."},
   "near_right":   {"x":, "y_bottom":, "where": ""},
   "far_left":     {"x":, "y_bottom":, "where": ""},
   "far_right":    {"x":, "y_bottom":, "where": ""}
 },
 "which_leg_is_back_left": "какая из ножек ближе всего к камере слева и при этом сзади",
 "ground_line_note": "как понять, где земля: по низу ножек?"
}
Только JSON."""

POET_Q = """На картинке — сидящий человек (спрайт визуальной новеллы) на светло-сером фоне.
Сетка: доли кадра, 0.0 слева/сверху, 1.0 справа/снизу. Человек в позе «сидит, локти на
коленях или руки у лица», ноги опущены вниз.

Нужны ТОЧНЫЕ доли по вертикали:
{
 "head_top_y": ,
 "seat_contact_y": "y той линии, где таз/ягодицы касаются сиденья (низ спины, самый низ
                    туловища перед началом бёдер)",
 "thigh_front_y": "y переднего края бёдер (где колени)",
 "feet_y": "y подошв",
 "body_left_x": , "body_right_x": ,
 "notes": "что видно"
}
Только JSON."""


def main():
    p = grid(os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp'),
             os.path.join(OUT, 'prop_grid.jpg'))
    j1 = ask(p, PROP_Q)
    if j1:
        print('--- PROP ---')
        print(json.dumps(j1, ensure_ascii=False, indent=2))
        with open(os.path.join(OUT, 'prop_measure.json'), 'w', encoding='utf-8') as f:
            json.dump(j1, f, ensure_ascii=False, indent=2)
    q = grid(os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp'),
             os.path.join(OUT, 'poet_grid.jpg'), bg=(235, 235, 235))
    j2 = ask(q, POET_Q)
    if j2:
        print('--- POET ---')
        print(json.dumps(j2, ensure_ascii=False, indent=2))
        with open(os.path.join(OUT, 'poet_measure.json'), 'w', encoding='utf-8') as f:
            json.dump(j2, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
