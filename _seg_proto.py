# -*- coding: utf-8 -*-
"""Прототип: разбор абзаца на РЕПЛИКУ и АВТОРСКИЙ текст.

Правило: маркер диалога — «— » в начале абзаца или после , . ? ! … : ;
(«— » внутри фразы без знака перед ним — обычное тире, не маркер).
Сегменты чередуются: реплика → автор → реплика ...
Авторская вставка, кончающаяся ЗАПЯТОЙ (реплика продолжается сразу), — это пауза
внутри реплики: приклеиваем её обратно к реплике, голос остаётся персонажа.
Вставка, кончающаяся ТОЧКОЙ, — отдельная авторская страница (голос закадра).
"""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
lines = open(os.path.join(HERE, "assets", "story.txt"), encoding="utf-8").read().split("\n")
L = {i + 1: ln.strip() for i, ln in enumerate(lines)}
reception_par = {n: L[n] for n in range(13, 68) if L.get(n) and not L[n].startswith("*")}

SENT = re.compile(r"(?<=[.!?…])\s+(?=[А-ЯA-Z«—])")


def segments(par):
    starts = []
    for m in re.finditer(r"—\s", par):
        i = m.start()
        if i == 0:
            starts.append((i, m.end()))
            continue
        prev = par[:i].rstrip()
        if prev and prev[-1] in ",.?!…:;":
            starts.append((i, m.end()))
    if not starts:
        return [("narr", par.strip())]
    out = []
    if starts[0][0] > 0:
        head = par[:starts[0][0]].strip()
        if head:
            out.append(("narr", head))
    for k, (i, end) in enumerate(starts):
        stop = starts[k + 1][0] if k + 1 < len(starts) else len(par)
        seg = par[end:stop].strip()
        if seg:
            out.append(("speech" if k % 2 == 0 else "narr", seg))
    # склейка авторских «пауз внутри реплики» (кончаются запятой) с предыдущей репликой
    merged = []
    for kind, tx in out:
        if merged and kind == "narr" and tx.rstrip().endswith(",") and merged[-1][0] == "speech":
            merged[-1] = ("speech", merged[-1][1] + " — " + tx)
        else:
            merged.append((kind, tx))
    return merged


def pages_of(segments_list, maxn=2):
    """Сегменты -> страницы, НИКОГДА не смешивая реплику и авторский текст."""
    out = []
    for kind, tx in segments_list:
        parts = [s.strip() for s in SENT.split(tx) if s.strip()]
        cur = []
        for s in parts:
            cur.append(s)
            if len(cur) >= maxn:
                out.append((kind, " ".join(cur))); cur = []
        if cur:
            out.append((kind, " ".join(cur)))
    return out


if __name__ == "__main__":
    n_pages = 0
    for n in sorted(reception_par):
        print("=== абзац", n)
        segs = segments(reception_par[n])
        for kind, tx in segs:
            print("   [%s] %s" % (kind, tx[:80]))
        for kind, tx in pages_of(segs):
            n_pages += 1
            print("      стр %-6s %s" % (kind, tx[:70]))
    print("\nвсего страниц:", n_pages)
