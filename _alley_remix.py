# -*- coding: utf-8 -*-
"""Пересборка музыкальных вариантов сцены «аллея» (правка Ивана 2026-11-06).

Что было не так: elevenlabs отдал «весеннюю улицу» на -55 dBFS (тишина), а старый mix()
дополнительно резал её на -13 dB — в alley_mix.mp3 улицы не было слышно совсем.

Теперь:
  • alley_mix.mp3 — тема + улица, улица нормализована до RMS -30 dBFS (~14 dB под темой);
  • alley_bed.mp3 — только тема (lyria-3-5);
  • alley_amb.mp3 — только улица, нормализована до RMS -28 dBFS (можно слушать отдельно).
Проверка после сборки: доля энергии >5 кГц в остатке (после вычета темы со сдвигом)
должна вырасти на порядки — значит улица реально в миксе.

Запуск: python3 _alley_remix.py [--target -30]
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUT = os.path.join(HERE, 'assets', 'audio', 'sketch')
SR = 44100


def pcm(path, ac=1, sr=SR):
    raw = subprocess.run([FF, '-hide_banner', '-v', 'error', '-i', path, '-f', 'f32le',
                          '-ac', str(ac), '-ar', str(sr), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def db(x):
    return 20 * np.log10(max(float(x), 1e-12))


def rms_db(x):
    return db(np.sqrt((x.astype(np.float64) ** 2).mean()))


def hf_share(x, k=SR * 20):
    seg = x[:k] if len(x) >= k else x
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    return float(sp[f > 5000].sum() / sp.sum())


target_mix = -30.0
if '--target' in sys.argv:
    target_mix = float(sys.argv[sys.argv.index('--target') + 1])

bed_src = os.path.join(OUT, 'alley_bed_0.mp4')
if not os.path.exists(bed_src):
    cand = sorted(f for f in os.listdir(OUT) if f.startswith('alley_bed_0.'))
    bed_src = os.path.join(OUT, cand[0])
amb_src = os.path.join(OUT, 'alley_amb_0.mp3')

rms_amb = rms_db(pcm(amb_src))
gain_mix = target_mix - rms_amb
gain_solo = -28.0 - rms_amb
print('bed: %s | amb RMS %.1f dBFS' % (os.path.basename(bed_src), rms_amb))
print('усиление улицы: в миксе %+.1f dB, отдельно %+.1f dB' % (gain_mix, gain_solo))

# --- микс: тема + улица (петля до длины темы), без renormalize; промежуточно в WAV
mix_wav = os.path.join(OUT, '_alley_mix_tmp.wav')
fc = ("[1:a]aloop=loop=-1:size=2e9,volume=%.2fdB,highpass=f=180,lowpass=f=12000,"
      "alimiter=limit=0.35:level=disabled,afade=t=in:st=0:d=2[amb];"
      "[0:a][amb]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
      "alimiter=limit=0.95:level=disabled[m]") % gain_mix
r = subprocess.run([FF, '-y', '-v', 'error', '-i', bed_src, '-i', amb_src, '-filter_complex', fc,
                    '-map', '[m]', '-c:a', 'pcm_s16le', mix_wav], capture_output=True, text=True)
print('mix rc', r.returncode, (r.stderr or '')[-300:])
if r.returncode:
    sys.exit(1)

# пик и громкость считаем по готовому WAV — без двойного mp3
peak = float(np.abs(pcm(mix_wav, ac=2)).max())
trim = 20 * np.log10(0.95 / peak) if peak > 0.95 else 0.0
mix_rms = rms_db(pcm(mix_wav, ac=1))
print('пик %.2f, RMS(моно) %.1f dBFS' % (peak, mix_rms))

# громкость как у темы приёмной: переключение сцен не должно щёлкать уровнем
ref = os.path.join(OUT, 'vn_reception_soft_0.mp3')
match = 0.0
if os.path.exists(ref):
    ref_rms = rms_db(pcm(ref, ac=1))
    match = ref_rms - mix_rms
    print('тема приёмной RMS %.1f -> подстройка %+.2f dB' % (ref_rms, match))
trim += match
vf = ('volume=%.2fdB,' % trim) if abs(trim) > 0.01 else ''

dst_mix = os.path.join(OUT, 'alley_mix.mp3')
r = subprocess.run([FF, '-y', '-v', 'error', '-i', mix_wav, '-af', (vf or 'anull'),
                    '-c:a', 'libmp3lame', '-b:a', '112k', '-ac', '2', dst_mix],
                   capture_output=True, text=True)
print('alley_mix.mp3 rc=%d %d Б  итог RMS %.1f dBFS  пик %.2f'
      % (r.returncode, os.path.getsize(dst_mix), rms_db(pcm(dst_mix, ac=1)),
         float(np.abs(pcm(dst_mix, ac=2)).max())))
if os.path.exists(mix_wav):
    os.remove(mix_wav)

# --- вариант «только тема» в той же громкости, чтобы A/B отличались только улицей
dst_bed = os.path.join(OUT, 'alley_bed.mp3')
bed_trim = match if os.path.exists(ref) else 0.0
r = subprocess.run([FF, '-y', '-v', 'error', '-i', bed_src,
                    '-af', ('volume=%.2fdB,alimiter=limit=0.95' % bed_trim) if bed_trim else
                           'alimiter=limit=0.95',
                    '-c:a', 'libmp3lame', '-b:a', '112k', '-ac', '2', dst_bed],
                   capture_output=True, text=True)
print('alley_bed.mp3 rc=%d RMS %.1f dBFS' % (r.returncode, rms_db(pcm(dst_bed))))

# --- только улица, вменяемый уровень
dst_amb = os.path.join(OUT, 'alley_amb.mp3')
r = subprocess.run([FF, '-y', '-v', 'error', '-i', amb_src,
                    '-af', 'volume=%.2fdB,highpass=f=180,lowpass=f=12000,alimiter=limit=0.9'
                           % gain_solo,
                    '-c:a', 'libmp3lame', '-b:a', '112k', '-ac', '2', dst_amb],
                   capture_output=True, text=True)
print('alley_amb.mp3 rc=%d %d Б  RMS %.1f dBFS'
      % (r.returncode, os.path.getsize(dst_amb), rms_db(pcm(dst_amb))))

# --- контроль: остаток после вычета темы должен содержать воздух
b = pcm(bed_src).astype(np.float64)
m = pcm(dst_mix).astype(np.float64)
n = min(len(b), len(m))
b, m = b[:n], m[:n]
best = (-1, -1e18)
for lag in range(0, 2001, 50):
    seg = m[SR:SR * 4]
    x = b[SR + lag:SR * 4 + lag]
    c = float(np.dot(seg, x))
    if c > best[1]:
        best = (lag, c)
lag = best[0]
b = np.roll(b, -lag)
res = m - (np.dot(m, b) / np.dot(b, b)) * b
print('сдвиг темы %d сэмплов, микс RMS %.1f dBFS' % (lag, rms_db(m)))
print('остаток RMS %.1f dBFS | доля >5 кГц: тема %.4f, остаток %.4f'
      % (rms_db(res), hf_share(b), hf_share(res)))
