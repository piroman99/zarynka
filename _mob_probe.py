# -*- coding: utf-8 -*-
"""Замер мобильной вёрстки vn2: где реально оказываются кнопки на титуле.
Проверяем портрет/ландшафт телефонов и десктоп, меряем рамки и снимаем скриншоты.
"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _cdp

URL = 'file://' + os.path.join(HERE, 'vn2', 'index.html')
OUTDIR = os.path.join(HERE, 'assets', 'review')

PROFILES = [
    # name, w, h, dpr, mobile
    ('desk_1440x900', 1440, 900, 1, False),
    ('port_390x844', 390, 844, 2, True),
    ('land_844x390', 844, 390, 2, True),
    ('port_360x800', 360, 800, 2, True),
    ('land_800x360', 800, 360, 2, True),
    ('land_932x430', 932, 430, 2, True),
    ('port_430x932', 430, 932, 2, True),
]

MEAS = r"""
(() => {
  const r = (el) => { if (!el) return null; const b = el.getBoundingClientRect();
    return {x:Math.round(b.x), y:Math.round(b.y), w:Math.round(b.width), h:Math.round(b.height),
            bottom:Math.round(b.bottom), right:Math.round(b.right)}; };
  const q = (s) => document.querySelector(s);
  const stage = r(document.getElementById('stage'));
  const vw = innerWidth, vh = innerHeight;
  const tin = q('#title .title-inner');
  const out = {
    vw: vw, vh: vh,
    stage: stage,
    inner: r(tin),
    innerScrollH: tin ? tin.scrollHeight : null,
    parts: {},
  };
  ['#title .logo', '#tt', '.sub', '#tep', '#start', '#pl', '#pltext', '#teaser', '#by'].forEach((s) => {
    out.parts[s] = r(q(s));
  });
  const t = out.parts['#teaser'];
  out.fit_scale = getComputedStyle(document.querySelector('#title .title-inner')).transform;
  out.teaser_visible = !!(t && t.y >= 0 && t.bottom <= vh && t.right <= vw && t.x >= 0);
  return out;
})()
"""

HUD_MEAS = r"""
(() => {
  const r = (el) => { if (!el) return null; const b = el.getBoundingClientRect();
    return {y:Math.round(b.y), h:Math.round(b.height), bottom:Math.round(b.bottom), w:Math.round(b.width)}; };
  const box = document.getElementById('box'), txt = document.getElementById('text');
  const b = r(box), t = r(txt);
  const fs = txt ? parseFloat(getComputedStyle(txt).fontSize) : null;
  const lines = txt ? Math.round(txt.getBoundingClientRect().height / (fs * 1.5)) : null;
  return {vw: innerWidth, vh: innerHeight, stage: r(document.getElementById('stage')),
          box: b, text: t, font: fs, lines: lines,
          box_fits: !!(b && b.bottom <= innerHeight && b.y >= 0)};
})()
"""


def run(node=None, tag=''):
    b = _cdp.Browser(1600, 900)
    res = {}
    try:
        for name, w, h, dpr, mob in PROFILES:
            b.send('Emulation.setDeviceMetricsOverride', width=w, height=h,
                   deviceScaleFactor=dpr, mobile=mob)
            extra = '&node=%d' % node if node is not None else ''
            b.navigate(URL + '?instant=1&text=1&voice=0&music=0&preload=0' + extra, wait=1.2)
            time.sleep(0.4)
            m = b.js(MEAS if node is None else HUD_MEAS)
            res[name] = m
            shot = os.path.join(OUTDIR, 'mob_probe%s_%s.png' % (tag, name))
            b.shot(shot)
            print(name, 'shot', os.path.getsize(shot), 'B')
    finally:
        b.close()
    return res


if __name__ == '__main__':
    node = None
    if len(sys.argv) > 1 and sys.argv[1] != 'title':
        node = int(sys.argv[1])
    tag = '' if node is None else '_node%d' % node
    data = run(node, tag)
    p = os.path.join(HERE, '.tmp_mob', 'probe%s.json' % tag)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(data, open(p, 'w'), ensure_ascii=False, indent=1)
    print('json:', os.path.relpath(p, HERE))
    if node is None:
        print('%-14s %-9s %-18s %s' % ('profile', 'viewport', 'stage', 'teaser y..bottom / visible'))
        for name, m in data.items():
            st = m['stage']
            t = m['parts']['#teaser']
            print('%-14s %-9s %-18s %s / %s' % (
                name, '%dx%d' % (m['vw'], m['vh']),
                'y%d h%d' % (st['y'], st['h']) if st else '-',
                ('y%d..%d' % (t['y'], t['bottom'])) if t else '-', m['teaser_visible']))
    else:
        print('%-14s %-9s %-16s %-16s %s' % ('profile', 'viewport', 'stage', 'box', 'font/lines/fits'))
        for name, m in data.items():
            st, bx = m['stage'], m['box']
            print('%-14s %-9s %-16s %-16s %s' % (
                name, '%dx%d' % (m['vw'], m['vh']),
                'y%d h%d' % (st['y'], st['h']) if st else '-',
                'y%d..%d h%d' % (bx['y'], bx['bottom'], bx['h']) if bx else '-',
                '%s/%s/%s' % (m['font'], m['lines'], m['box_fits'])))
