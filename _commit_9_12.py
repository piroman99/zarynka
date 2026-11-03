# -*- coding: utf-8 -*-
"""Коммит и пуш кадров 9-12 (плотная сетка) + титр-слой + переозвучка."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(os.path.dirname(HERE))
KEY = os.path.join(WS, '.ssh', 'github_ed25519')
KNOWN = os.path.join(WS, '.ssh', 'known_hosts')
env = dict(os.environ)
env['GIT_SSH_COMMAND'] = ('ssh -i %s -o IdentitiesOnly=yes -o UserKnownHostsFile=%s '
                          '-o StrictHostKeyChecking=no' % (KEY, KNOWN))

FILES = [
    'PROLOG_BRIEF_9_12.md', 'STATUS.md',
    '_prolog_finals.py', '_vn2_build.py',
    'vn2/app.js', 'vn2/content.js', 'vn2/index.html', 'vn2/style.css',
    'assets/final/prolog/s3.png', 'assets/final/prolog/s4.png',
    'assets/final/prolog/s5.png', 'assets/final/prolog/s5a.png',
    'vn2/img/prolog/s3.webp', 'vn2/img/prolog/s4.webp',
    'vn2/img/prolog/s5.webp', 'vn2/img/prolog/s5a.webp',
    'vn2/audio/vo/s5a_00.mp3', 'vn2/audio/vo/s5a_01.mp3', 'vn2/audio/vo/s5b_00.mp3',
    'vn2/audio/vo/s5_00.mp3', 'vn2/audio/vo/s5_01.mp3',   # удаления
    'vn2/audio/vo/_voices.json',
    'assets/gen/s5a_a__gpt-image-2_0.png', 'assets/gen/s5a_b__gpt-image-2_0.png',
    '_prolog_vo_s5ab.py', '_vo_drop_old_s5.py', '_voices_sync_prolog.py',
    '_vn2_vo_prolog_check.py',
    '_ovl_fit.py', '_ovl_shots.py', '_ovl_sheet_small.py', '_ovl_metrics.py',
    '_probe_ovl_dom.py', '_clean_ovl_scratch.py',
    '_prolog_check_9_10_12.py', '_prolog_s5a.py', '_prolog_s5a_sheet.py',
    '_s5a_band.py', '_s5a_band2.py', '_s5a_grid.py', '_s5a_measure.py',
    '_s5ab_map.py', '_voices_peek.py',
    '_sat/ovl_shots.png', '_sat/ovl_sheet_small.jpg', '_sat/sheet_s5a.png',
    '_sat/crops_s5a.png', '_sat/s5a_a_grid.png', '_sat/s5a_band_v2.png',
    '_sat/check_9_10_12.png', '_sat/check_9_10_12_tags.png',
]

r = subprocess.run(['git', 'add', '--'] + FILES, capture_output=True, text=True)
print('add rc', r.returncode, r.stderr[-300:])
r = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print('\n'.join(l for l in r.stdout.splitlines() if l[:2] in ('M ', 'A ', 'D ', 'MM'))[:2000])

MSG = ('vn2: пролог — кадры 9-12 (плотная сетка), титр-слой по страницам, переозвучка\n\n'
       '9 s3: плашка и строки убраны из PNG, только метка (0 руб)\n'
       '10 s4: подпись снята с экрана панели, метка РОЛИК (0 руб)\n'
       '11 s5a: новый кадр — площадь с плакатными тумбами (вариант A)\n'
       '12 s5b: ТРИУМФ без полосы лозунга и чипа (0 руб)\n'
       'Текст SEG9[2] разрезан по фразе Волна требований: s5a 2 стр + s5b 1 стр.\n'
       'Надписи живут в титр-слое движка (pg.ovl), страница = фраза.\n'
       'Озвучка s5a_00/s5a_01/s5b_00 записана (0.79 руб), VO_VER 5, пролог 14 стр/129.9 с.')
r = subprocess.run(['git', 'commit', '-m', MSG], capture_output=True, text=True)
print('commit rc', r.returncode, r.stdout[-500:], r.stderr[-300:])
r = subprocess.run(['git', 'push', 'origin', 'HEAD:rebuild'], capture_output=True, text=True,
                   env=env, timeout=300)
print('push rc', r.returncode, r.stdout[-300:], r.stderr[-300:])
r = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True)
print('HEAD', r.stdout.strip())
