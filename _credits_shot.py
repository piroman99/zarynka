# -*- coding: utf-8 -*-
"""Титры: скриншоты (десктоп/портрет) + честная проверка движка через CDP.

Проверяем: экран титров открывается кнопкой на экране конца серии, список
рендерится из content.js (window.VN.credits), блок прокручивается, «Назад»
и Escape закрывают, JS-ошибок нет, листание страницей не срабатывает.
"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

OUT = os.path.join(HERE, 'assets', 'review')
URL = 'file://' + os.path.join(HERE, 'vn2', 'index.html') + '?node=0&instant=1&voice=0&music=0'
os.makedirs(OUT, exist_ok=True)

def run(w, h, tag):
    b = Browser(w, h)
    try:
        b.navigate(URL, wait=1.2)
        # экран конца серии включён принудительно (без 126 кликов), кнопки берём настоящие
        b.js("document.getElementById('end').classList.add('show')")
        time.sleep(0.7)
        b.shot(os.path.join(OUT, 'review_112_credits_%s_end.png' % tag))
        btns = b.js("Array.from(document.querySelectorAll('#end .endbtns button')).map(b=>({id:b.id,tx:b.textContent.trim(),vis:!!(b.offsetWidth&&b.offsetHeight)}))")
        # открываем титры настоящим кликом по кнопке
        b.js("document.getElementById('e-credits').click()")
        time.sleep(0.9)
        st = b.js("(function(){var s=document.getElementById('credits'),i=document.querySelector('.cr-inner');"
                  "return {open:s.classList.contains('show'),aria:s.getAttribute('aria-hidden'),"
                  "groups:document.querySelectorAll('#crlist .crgrp').length,"
                  "rows:document.querySelectorAll('#crlist .crrow').length,"
                  "notes:document.querySelectorAll('#crlist .crnote').length,"
                  "scrollH:i.scrollHeight,clientH:i.clientHeight,"
                  "txt:document.getElementById('crlist').innerText.slice(0,400)};})()")
        b.shot(os.path.join(OUT, 'review_112_credits_%s_open.png' % tag))
        # пролистать до низа и снять ещё раз, если не влезает
        scrolled = b.js("(function(){var i=document.querySelector('.cr-inner');i.scrollTop=i.scrollHeight;"
                        "return i.scrollTop;})()")
        rect = b.js("(function(){var b=document.getElementById('cr-back').getBoundingClientRect(),"
                    "i=document.querySelector('.cr-inner').getBoundingClientRect();"
                    "return {btn:[Math.round(b.left),Math.round(b.top),Math.round(b.right),Math.round(b.bottom)],"
                    "inner:[Math.round(i.left),Math.round(i.top),Math.round(i.right),Math.round(i.bottom)],"
                    "vw:innerWidth,vh:innerHeight};})()")
        if scrolled:
            time.sleep(0.4)
            b.shot(os.path.join(OUT, 'review_112_credits_%s_bottom.png' % tag))
        # позиция в новелле не должна меняться от клика внутри титров
        pos0 = b.js("window.__DBG.pos")
        b.js("document.querySelector('.cr-inner').click()")
        time.sleep(0.3)
        pos1 = b.js("window.__DBG.pos")
        # закрытие кнопкой «Назад»
        b.js("document.getElementById('cr-back').click()")
        time.sleep(0.6)
        closed = b.js("document.getElementById('credits').classList.contains('show')")
        # и ещё раз — через Escape
        b.js("document.getElementById('e-credits').click()")
        time.sleep(0.5)
        b.js("window.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}))")
        time.sleep(0.4)
        closed_esc = b.js("document.getElementById('credits').classList.contains('show')")
        errs = [e for e in b.errors()
                if 'manifest.webmanifest' not in e and 'ERR_FAILED' not in e]  # file:// CORS манифеста — не наша ошибка
        print('== %s %dx%d' % (tag, w, h))
        print('  кнопки конца:', json.dumps(btns, ensure_ascii=False))
        print('  титры:', json.dumps({k: v for k, v in st.items() if k != 'txt'}, ensure_ascii=False),
              'скролл:', scrolled, 'поз:', pos0, '->', pos1)
        print('  закрытие: Назад=%s Escape=%s  JS-ошибки: %s' % (not closed, not closed_esc, errs or 'нет'))
        print('  рамки:', json.dumps(rect, ensure_ascii=False))
        print('  текст:', (st.get('txt') or '').replace('\n', ' / ')[:300])
        return {'btns': btns, 'st': st, 'scrolled': scrolled, 'pos': (pos0, pos1), 'rect': rect,
                'closed_back': not closed, 'closed_esc': not closed_esc, 'errs': errs}
    finally:
        b.close()

res = {}
for tag, w, h in [('desk', 1600, 900), ('port', 390, 844), ('land', 844, 390)]:
    res[tag] = run(w, h, tag)

ok = True
for tag, r in res.items():
    st = r['st']
    cond = (st['open'] and st['groups'] == 3 and st['rows'] == 8 and st['notes'] == 1
            and any(b['id'] == 'e-credits' and b['vis'] for b in r['btns'])
            and r['pos'][0] == r['pos'][1]
            and r['closed_back'] and r['closed_esc'] and not r['errs'])
    # рамки: блок и кнопка «Назад» не выходят за вьюпорт
    rc = r['rect']
    box_ok = (0 <= rc['inner'][0] and rc['inner'][2] <= rc['vw']
              and 0 <= rc['inner'][1] and rc['inner'][3] <= rc['vh']
              and rc['btn'][1] >= rc['inner'][1] - 1 and rc['btn'][3] <= rc['vh'])
    cond = cond and box_ok
    print('%-5s %s' % (tag, 'OK' if cond else 'FAIL'))
    ok = ok and cond
print('ИТОГ:', 'ОК' if ok else 'ПРОВАЛ')
sys.exit(0 if ok else 1)
