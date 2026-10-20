# -*- coding: utf-8 -*-
"""Общее для проверок озвучки: чтение content.js и разбор страниц на СЕГМЕНТЫ.

С 2026-10-21 у склеенной страницы («— Спасибо, — от улыбки…») ДВА голоса:
  pg.vo   = ["audio/vo/rec_22.mp3", "audio/vo/rec_22b.mp3"]
  pg.vtx  = ["— Спасибо,", "от улыбки вокруг её глаз разбежались морщинки,"]
  pg.vwho = ["Екатерина", "narr"]
У обычной страницы vo — строка. Все проверки ходят через segments(), чтобы
не дублировать эту логику.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(HERE, 'vn2')
VO = os.path.join(VN2, 'audio', 'vo')
MAN = os.path.join(VO, '_voices.json')


def load_content():
    src = open(os.path.join(VN2, 'content.js'), encoding='utf-8').read()
    return json.loads(src[src.index('{'):src.rindex('}') + 1])


def load_manifest():
    return json.load(open(MAN, encoding='utf-8'))


def segs_of(pg):
    """Страница -> [(файл, текст сегмента, кто)]."""
    vo = pg.get('vo')
    if not vo:
        return []
    vos = [vo] if isinstance(vo, str) else list(vo)
    vtx = pg.get('vtx') or [pg['tx']] * len(vos)
    vwho = pg.get('vwho') or [pg.get('who') or 'narr'] * len(vos)
    return [(vos[i], vtx[i] if i < len(vtx) else pg['tx'],
             (vwho[i] if i < len(vwho) else 'narr') or 'narr') for i in range(len(vos))]


def segments(content):
    """Все сегменты эпизода: [(узел, номер страницы, файл, текст, кто)]."""
    out = []
    for nd in content['nodes']:
        nid = nd.get('id') or nd.get('t')
        for k, pg in enumerate(nd.get('pages') or []):
            for vo, tx, who in segs_of(pg):
                out.append((nid, k, vo, tx, who))
    return out


def norm(t):
    """Нормализация для сравнения «текст страницы == озвученный текст»."""
    t = (t or '').replace('«', '"').replace('»', '"')
    t = t.replace('—', '-').replace('–', '-').replace('…', '...')
    t = re.sub(r'^[-\s]+', '', t)
    t = re.sub(r'[^0-9A-Za-zА-Яа-яЁё]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip().lower()
