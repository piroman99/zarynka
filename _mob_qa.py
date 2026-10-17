# -*- coding: utf-8 -*-
"""QA мобильной вёрстки vn2: не только рамки, но и «а реально ли нарисовано».
Для каждого профиля: титул (кнопка «Тизер» в кадре + красная заливка под ней)
и игровой узел s1 (подстрочник читаемого кегля, не обрезан).
"""
import os, sys, json, time
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _cdp

URL = 'file://' + os.path.join(HERE, 'vn2', 'index.html')
OUT = os.path.join(HERE, '.tmp_mob')
os.makedirs(OUT, exist_ok=True)

PROFILES = [
    ('desk_1440x900', 1440, 900, 1, False),
    ('port_390x844', 390, 844, 2, True),
    ('port_430x932', 430, 932, 2, True),
    ('port_360x800', 360, 800, 2, True),
    ('land_844x390', 844, 390, 2, True),
    ('land_932x430', 932, 430, 2, True),
    ('land_800x360', 800, 360, 2, True),
]

RECTS = r"""
(() => {
  const r = (s) => { const el = document.querySelector(s); if (!el) return null;
    const b = el.getBoundingClientRect();
    return [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)]; };
  const b = document.querySelector('#box'); const bs = b ? getComputedStyle(b) : null;
  const t = document.querySelector('#text');
  return {
    vw: innerWidth, vh: innerHeight,
    stage: r('#stage'), teaser: r('#teaser'), start: r('#start'), logo: r('#title .logo'),
    by: r('#by'), tools: r('#tools'), box: r('#box'), text: r('#text'),
    font: t ? parseFloat(getComputedStyle(t).fontSize) : null,
    boxTop: bs ? bs.top : null,
    scale: getComputedStyle(document.querySelector('#title .title-inner')).transform,
    dpr: devicePixelRatio,
  };
})()
"""


def red_at(img, rect, dpr):
    """Доля «красных» пикселей в прямоугольнике (CSS-координаты)."""
    x, y, w, h = [int(v * dpr) for v in rect]
    x, y = max(0, x), max(0, y)
    crop = img.crop((x, y, min(img.width, x + w), min(img.height, y + h))).convert('RGB')
    px = list(crop.getdata())
    if not px:
        return 0.0
    red = sum(1 for (r, g, b) in px if r > 140 and r > g + 40 and r > b + 40)
    return red / len(px)


def bright_at(img, rect, dpr):
    x, y, w, h = [int(v * dpr) for v in rect]
    x, y = max(0, x), max(0, y)
    crop = img.crop((x, y, min(img.width, x + w), min(img.height, y + h))).convert('RGB')
    px = list(crop.getdata())
    if not px:
        return 0.0
    br = sum(1 for (r, g, b) in px if r + g + b > 540)
    return br / len(px)


def run():
    b = _cdp.Browser(1600, 900)
    rows = []
    try:
        for name, w, h, dpr, mob in PROFILES:
            b.send('Emulation.setDeviceMetricsOverride', width=w, height=h,
                   deviceScaleFactor=dpr, mobile=mob)
            row = {'profile': name, 'vp': '%dx%d' % (w, h)}

            # --- титул ---
            b.navigate(URL + '?instant=1&text=1&voice=0&music=0&preload=0', wait=1.3)
            time.sleep(0.3)
            m = b.js(RECTS)
            shot = os.path.join(OUT, 'qa_title_%s.png' % name)
            b.shot(shot)
            img = Image.open(shot)
            t = m['teaser']
            inside = bool(t and t[0] >= 0 and t[1] >= 0 and t[0] + t[2] <= w and t[1] + t[3] <= h)
            row['title_teaser_inside'] = inside
            row['title_teaser_red'] = round(red_at(img, t, dpr), 3) if t else 0
            row['title_scale'] = m['scale']
            row['title_logo_in'] = bool(m['logo'] and m['logo'][1] >= 0)
            row['title_by'] = m['by']

            # --- игровой узел s1 (индекс 2) ---
            b.navigate(URL + '?instant=1&text=1&voice=0&music=0&preload=0&node=2', wait=1.6)
            time.sleep(0.3)
            g = b.js(RECTS)
            shot2 = os.path.join(OUT, 'qa_s1_%s.png' % name)
            b.shot(shot2)
            img2 = Image.open(shot2)
            bx, tx = g['box'], g['text']
            row['s1_stage'] = '%dx%d@%d' % (g['stage'][2], g['stage'][3], g['stage'][1])
            row['s1_box'] = 'y%d h%d' % (bx[1], bx[3]) if bx else None
            row['s1_font'] = g['font']
            row['s1_box_in_vp'] = bool(bx and bx[1] >= 0 and bx[1] + bx[3] <= h + 1)
            row['s1_text_ink'] = round(bright_at(img2, tx, dpr), 4) if tx else 0
            row['s1_text_fits'] = bool(tx and bx and tx[1] + tx[3] <= bx[1] + bx[3] + 1)
            rows.append(row)
    finally:
        errs = [e for e in b.errors() if 'fullscreen' not in e.lower()]
        b.close()
    return rows, errs


if __name__ == '__main__':
    rows, errs = run()
    json.dump(rows, open(os.path.join(OUT, 'qa.json'), 'w'), ensure_ascii=False, indent=1)
    keys = ['profile', 'vp', 'title_teaser_inside', 'title_teaser_red', 'title_logo_in',
            's1_box', 's1_font', 's1_box_in_vp', 's1_text_ink', 's1_text_fits', 'title_scale']
    print(' | '.join(keys))
    for r in rows:
        print(' | '.join(str(r.get(k)) for k in keys))
    print('errors:', errs)
