#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Подстрочник эп-1: текст каждой страницы VN с ярлыком того, КТО её читает.

Зачем: проверять «озвучка = текст» глазами и ушами, не листая новеллу.
Пишет три файла:
  out/ep1_script.md   — читаемая таблица: №, сцена, голос, файл, текст
  out/ep1_script.srt  — субтитры к склейке (ярлык голоса + текст страницы)
  out/ep1_vo_full.mp3 — вся озвучка подряд, с паузами между страницами

Запуск: python3 _vn2_script.py [--no-audio]
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
VN2 = os.path.join(HERE, 'vn2')
VD = os.path.join(VN2, 'audio', 'vo')
OUT = os.path.join(HERE, 'out')
import _vo_util as U   # разбор страниц на сегменты (склеенная страница = 2 голоса)
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')

LABEL = {'narr': 'АВТОР', 'Старик': 'СТАРИК', 'Сергей': 'СЕРГЕЙ',
         'Екатерина': 'ЕКАТЕРИНА'}
SCENE = {'s1': 'Пролог · подворотня', 's2': 'Пролог · Звёздный городок',
         's3': 'Пролог · «а обычных людей нет?»', 's4': 'Пролог · ролик',
         's5': 'Пролог · лозунг', 's6': 'Пролог · очередь',
         's7': 'Пролог · приёмная (крыльцо)', 'starik': 'Кабинет Старика',
         'reception': 'Приёмная комиссия'}
GAP_PAGE = 0.45      # пауза между страницами, с
GAP_NODE = 1.6       # пауза между сценами, с


def dur(path):
    out = subprocess.run([FF, '-hide_banner', '-i', path],
                         capture_output=True, text=True).stderr
    for line in out.splitlines():
        if 'Duration:' in line:
            h, m, s = line.split('Duration:')[1].split(',')[0].strip().split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise SystemExit('не прочитать длительность: ' + path)


def srt_t(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


def main():
    src = open(os.path.join(VN2, 'content.js'), encoding='utf-8').read()
    D = json.loads(src[src.index('{'):src.rindex('}') + 1])
    man = json.load(open(os.path.join(VD, '_voices.json'), encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)

    rows, n = [], 0
    for nd in D['nodes']:
        if nd.get('t') != 'scene':
            continue
        nid = nd.get('id')
        for k, pg in enumerate(nd.get('pages') or []):
            for j, (vo, stx, who) in enumerate(U.segs_of(pg)):
                n += 1
                path = os.path.join(VN2, vo)
                rows.append({
                    'no': n, 'node': nid, 'first': k == 0 and j == 0, 'idx': k,
                    'who': who,
                    'voice': (man.get(vo) or {}).get('voice') or who,
                    'file': os.path.basename(vo),
                    'tx': stx, 'dur': dur(path) if os.path.exists(path) else 0.0,
                })

    # --- md ---
    md = ['# «Зарянка» · эп-1 — подстрочник', '',
          'Ярлык = чей голос звучит на странице: **АВТОР** (закадр Charon), '
          '**СТАРИК** (Fenrir), **СЕРГЕЙ** (Charon), **ЕКАТЕРИНА** (Charlotte).', '']
    cur = None
    for r in rows:
        if r['node'] != cur:
            cur = r['node']
            md += ['', '## %s  `%s`' % (SCENE.get(cur, cur), cur), '',
                   '| № | голос | файл | текст |', '|---|---|---|---|']
        md.append('| %d | %s | `%s` | %s |'
                  % (r['no'], LABEL[r['who']], r['file'],
                     r['tx'].replace('|', '\\|')))
    open(os.path.join(OUT, 'ep1_script.md'), 'w', encoding='utf-8').write(
        '\n'.join(md) + '\n')

    # --- srt + склейка ---
    cues, t = [], 0.0
    for r in rows:
        if r['first']:
            t += GAP_NODE if r['no'] > 1 else 0.0
        start = t
        t += r['dur'] + GAP_PAGE
        head = '[%s]' % LABEL[r['who']]
        if r['first']:
            head = '〔%s〕 %s' % (SCENE.get(r['node'], r['node']), head)
        cues.append((start, start + r['dur'], head + ' ' + r['tx']))
    with open(os.path.join(OUT, 'ep1_script.srt'), 'w', encoding='utf-8') as f:
        for i, (a, b, tx) in enumerate(cues, 1):
            f.write('%d\n%s --> %s\n%s\n\n' % (i, srt_t(a), srt_t(b), tx))

    if '--no-audio' in sys.argv:
        print('подстрочник: %d страниц -> out/ep1_script.md, out/ep1_script.srt'
              % len(rows))
        return

    # --- склейка всей озвучки подряд ---
    parts, sil = [], {}
    for g in sorted({GAP_PAGE, GAP_NODE}):
        p = os.path.join(OUT, '_sil_%03d.mp3' % int(g * 1000))
        subprocess.run([FF, '-y', '-f', 'lavfi', '-i',
                        'anullsrc=r=44100:cl=mono', '-t', '%.2f' % g,
                        '-c:a', 'libmp3lame', '-b:a', '96k', p],
                       capture_output=True)
        sil[g] = p
    for r in rows:
        if r['first'] and r['no'] > 1:
            parts.append(sil[GAP_NODE])
        parts.append(os.path.join(VN2, 'audio', 'vo', r['file']))
        parts.append(sil[GAP_PAGE])
    args = [FF, '-y']
    for p in parts:
        args += ['-i', p]
    graph = ''.join('[%d:a]' % i for i in range(len(parts)))
    graph += 'concat=n=%d:v=0:a=1[out]' % len(parts)
    args += ['-filter_complex', graph, '-map', '[out]',
             '-ar', '44100', '-ac', '1', '-b:a', '96k',
             os.path.join(OUT, 'ep1_vo_full.mp3')]
    subprocess.run(args, capture_output=True, check=True)
    for p in sil.values():
        os.remove(p)
    total = dur(os.path.join(OUT, 'ep1_vo_full.mp3'))
    print('подстрочник: %d страниц, озвучка %.1f с (%.1f мин)'
          % (len(rows), total, total / 60))
    print('  out/ep1_script.md · out/ep1_script.srt · out/ep1_vo_full.mp3')


if __name__ == '__main__':
    main()
