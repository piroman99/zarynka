# -*- coding: utf-8 -*-
"""Убить зависшие параллельные пересборки аниматика и запустить ОДИН чистый рендер в фоне.
Лог пишем в _anim_run.log — следим за ним файловыми инструментами (не exec_session)."""
import os, sys, signal, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, '.tmp_animatic')

# 1) найти и убить все *_prolog_animatic.py + оставшиеся ffmpeg-кодировщики silent
pids = []
for pat in ('_prolog_animatic.py', 'prolog_silent.mp4'):
    r = subprocess.run(['pgrep', '-af', pat], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        pid = line.split()[0]
        if pid.isdigit() and int(pid) != os.getpid():
            pids.append(int(pid))
print('found pids:', sorted(set(pids)))
for pid in sorted(set(pids)):
    try:
        os.kill(pid, signal.SIGKILL)
        print('killed', pid)
    except Exception as e:
        print('kill fail', pid, e)
time.sleep(1.5)
r = subprocess.run(['pgrep', '-af', '_prolog_animatic.py'], capture_output=True, text=True)
print('remaining:', r.stdout.strip() or 'none')

# 2) убрать битый частичный silent (писался несколькими процессами)
sp = os.path.join(TMP, 'prolog_silent.mp4')
if os.path.exists(sp):
    os.remove(sp); print('removed partial', os.path.relpath(sp, HERE))

# 3) запустить один чистый рендер в отдельной сессии (переживёт конец exec-сессии)
logp = os.path.join(HERE, '_anim_run.log')
log = open(logp, 'w')
p = subprocess.Popen(['python3', '-u', '_prolog_animatic.py'], cwd=HERE,
                     stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
print('started pid', p.pid, '-> _anim_run.log')
