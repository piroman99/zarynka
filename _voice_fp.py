# -*- coding: utf-8 -*-
"""Отпечаток голоса: каким голосом РЕАЛЬНО записан файл.

Зачем: манифест может врать (переиспользование копировало чужие файлы), а на слух
проверять 73 страницы долго. Здесь — акустический отпечаток:
  * F0 (медиана/25/75 перцентили, с поправкой на октавные ошибки);
  * LTAS — усреднённый спектр в 24 мел-полосах (нормированный), косинусная
    близость к центроидам голосов (narr/Старик/Сергей — мужские Charon/Fenrir,
    Екатерина — женский Charlotte).
Итог: для каждой страницы «чей голос звучит» по отпечатку vs «чей должен».

  python3 _voice_fp.py            # отчёт по всем файлам
  python3 _voice_fp.py --pages    # только расхождения с content.js
"""
import os, json, wave, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(HERE, 'vn2', 'audio', 'vo')
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')
SR = 16000
NB = 24

def pcm(path):
    tmp = path + '.fp.wav'
    subprocess.run([FF, '-y', '-i', path, '-ac', '1', '-ar', str(SR), tmp],
                   capture_output=True, text=True)
    w = wave.open(tmp)
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    w.close()
    os.remove(tmp)
    return a

def mel(f):
    return 2595 * np.log10(1 + f / 700.0)

def imel(m):
    return 700 * (10 ** (m / 2595.0) - 1)

EDGES = imel(np.linspace(mel(120), mel(3400), NB + 1))

def analyze(path):
    a = pcm(path)
    n = int(0.04 * SR); hop = int(0.02 * SR)
    lo, hi = int(SR / 320), int(SR / 70)
    f0s, spec = [], np.zeros(NB)
    frames = 0
    win = np.hanning(512)
    for i in range(0, max(0, len(a) - n), hop):
        fr = a[i:i + n]
        if np.sqrt((fr ** 2).mean()) < 0.015:
            continue
        fr = fr - fr.mean()
        c = np.correlate(fr, fr, 'full')[n - 1:]
        c /= (c[0] + 1e-9)
        seg = c[lo:hi]
        if len(seg):
            k = int(np.argmax(seg)) + lo
            if c[k] > 0.30:
                f0s.append(SR / k)
        # LTAS по 512-точечному окну
        x = np.pad(fr, (0, max(0, 512 - len(fr))))[:512] * win
        P = np.abs(np.fft.rfft(x)) ** 2
        freqs = np.fft.rfftfreq(512, 1.0 / SR)
        band = np.zeros(NB)
        for b in range(NB):
            m = (freqs >= EDGES[b]) & (freqs < EDGES[b + 1])
            band[b] = P[m].sum() + 1e-12
        spec += np.log(band)
        frames += 1
    if not frames:
        return None
    lt = spec / frames
    lt -= lt.mean()
    lt /= (np.linalg.norm(lt) + 1e-9)
    f0s = np.array(f0s) if f0s else np.array([0.0])
    # октавная поправка: приводим к 80..300 Гц
    f = f0s.copy()
    for _ in range(3):               # октавные ошибки: 40 -> 80 -> 160
        lo80 = f < 80
        if not lo80.any():
            break
        f[lo80] *= 2
    f = f[(f >= 80) & (f <= 320)]
    q = np.percentile(f, [25, 50, 75]) if len(f) else np.array([0, 0, 0])
    return {'f0': q, 'ltas': lt, 'frames': frames}

def load_pages():
    src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
    return json.loads(src[src.index('=') + 1:].strip().rstrip(';'))

def segs_of(pg):
    vo = pg.get('vo')
    if not vo:
        return []
    vos = [vo] if isinstance(vo, str) else list(vo)
    vtx = pg.get('vtx') or [pg['tx']] * len(vos)
    vwho = pg.get('vwho') or [pg.get('who') or 'narr'] * len(vos)
    return [(vos[i], vtx[i] if i < len(vtx) else pg['tx'], vwho[i]) for i in range(len(vos))]

def main():
    D = load_pages()
    man = json.load(open(os.path.join(VO, '_voices.json'), encoding='utf-8'))
    pages = []
    for nd in D['nodes']:
        for i, pg in enumerate(nd.get('pages') or []):
            for vo, tx, who in segs_of(pg):
                pages.append((nd.get('id'), i, vo, tx, who))
    res, cache = [], {}
    for nid, i, vo, tx, who in pages:
        p = os.path.join(HERE, 'vn2', vo)
        if not os.path.exists(p):
            continue
        if p not in cache:
            cache[p] = analyze(p)
        a = cache[p]
        if not a:
            continue
        res.append({'node': nid, 'idx': i, 'vo': vo, 'tx': tx, 'who': who,
                    'f0': a['f0'], 'ltas': a['ltas'], 'frames': a['frames'],
                    'man': (man.get(vo) or {}).get('voice')})
    # центроиды по «доверенным» файлам: голос из манифеста и пол совпадает с F0
    male = {'narr', 'Старик', 'Сергей'}
    groups = {'m': [], 'f': []}
    for r in res:
        f = r['f0'][1]
        if not f:
            continue
        if r['man'] in male and f < 150:
            groups['m'].append(r['ltas'])
        elif r['man'] == 'Екатерина' and f > 160:
            groups['f'].append(r['ltas'])
    C = {k: np.mean(v, axis=0) for k, v in groups.items() if v}
    print('центроиды: m=%d файлов, f=%d файлов' % (len(groups['m']), len(groups['f'])))
    bad = 0
    for r in res:
        sim = {k: float(np.dot(r['ltas'], C[k])) for k in C}
        guess = 'f' if sim.get('f', -9) > sim.get('m', -9) else 'm'
        want = 'f' if r['who'] == 'Екатерина' else 'm'
        ok = guess == want
        if not ok:
            bad += 1
        if not ok or '--all' in sys.argv:
            print('%-9s стр.%2d %-14s должен %-9s F0=%5.0f Гц  отпечаток=%s (m %.2f / f %.2f) %s'
                  % (r['node'], r['idx'], os.path.basename(r['vo']), r['who'],
                     r['f0'][1], guess, sim.get('m', 0), sim.get('f', 0),
                     '' if ok else '<<< НЕ ТОТ ГОЛОС'))
    print('\nстраниц: %d, расхождений по отпечатку: %d' % (len(res), bad))

main()
