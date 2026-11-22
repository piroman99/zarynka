# -*- coding: utf-8 -*-
"""Разбор абзаца рассказа на СЕГМЕНТЫ (реплика / авторский текст).

Вынесено из `_vn2_build.py`, чтобы этим же кодом пользовался подстрочник
(`_story_cast.py`), не запуская сборку VN целиком.

Правила (проверены на баге 2026-10-20 «озвучка разъехалась с текстом»):
  * маркер диалога — «— » в начале абзаца или ПОСЛЕ , . ? ! … : ;
    (тире внутри фразы без знака перед ним — обычное тире, не маркер);
  * авторская вставка ВНУТРИ реплики — отдельный сегмент, её читает закадр;
  * реплика короче STUB («Спасибо,» / «Простите,») склеивается со следующей
    авторской вставкой в ОДНУ страницу с ДВУМЯ голосами (kind='mix').
"""
import re

SENT = re.compile(r'(?<=[.!?…])\s+(?=[А-ЯA-Z«—])')
STUB = 15          # реплика короче — «обрывок»: склеивается с авторской вставкой


def segments(par):
    """Абзац -> [('speech'|'narr', текст)] или [('mix', [(kind, текст), ...])].

    Маркер диалога — «— » в начале абзаца или после ЗНАКА КОНЦА предложения
    ( . ! ? … : ; ). Тире после ЗАПЯТОЙ считается маркером только если в абзаце
    уже есть реплика — тогда это продолжение реплики после авторской вставки.
    Иначе это тире внутри фразы: «...отдавать своё в чужую епархию, — это было
    для него слишком болезненно» (найдено 2026-10-21 при разметке всего рассказа:
    старое правило принимало такую фразу за речь персонажа).
    """
    dashes = [(m.start(), m.end()) for m in re.finditer(r'—\s', par)]
    strong = []
    for i, end in dashes:
        prev = par[:i].rstrip()
        if not prev or prev[-1] in '.?!…:;':
            strong.append((i, end))
    if not strong:
        return [('narr', par.strip())]
    starts = list(strong)
    for i, end in dashes:
        if (i, end) in starts:
            continue
        prev = par[:i].rstrip()
        if prev and prev[-1] == ',':
            starts.append((i, end))
    starts.sort()
    out = []
    if starts[0][0] > 0:
        head = par[:starts[0][0]].strip()
        if head:
            out.append(('narr', head))
    for k, (i, end) in enumerate(starts):
        stop = starts[k + 1][0] if k + 1 < len(starts) else len(par)
        seg = par[end:stop].strip()
        if seg:
            out.append(('speech' if k % 2 == 0 else 'narr', seg))
    # ОБРЫВОК РЕПЛИКИ склеиваем с идущей следом авторской вставкой в одну страницу;
    # голоса при этом разные (реплика — персонаж, вставка — закадр), поэтому 'mix'.
    merged = []
    i = 0
    while i < len(out):
        kind, tx = out[i]
        if (kind == 'speech' and len(tx) <= STUB and i + 1 < len(out)
                and out[i + 1][0] == 'narr'):
            merged.append(('mix', [(kind, tx), (out[i + 1][0], out[i + 1][1])]))
            i += 2
            continue
        merged.append((kind, tx))
        i += 1
    return merged


def pages_of(segs, maxn=2):
    """Сегменты -> страницы по 1-2 предложения, НИКОГДА не смешивая
    реплику и авторский текст в одной странице (кроме склеенных 'mix')."""
    out = []
    for kind, tx in segs:
        if kind == 'mix':
            out.append(('mix', tx))
            continue
        cur = []
        for s in [x.strip() for x in SENT.split(tx) if x.strip()]:
            cur.append(s)
            if len(cur) >= maxn:
                out.append((kind, ' '.join(cur)))
                cur = []
        if cur:
            out.append((kind, ' '.join(cur)))
    return out
