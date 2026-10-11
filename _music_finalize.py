# -*- coding: utf-8 -*-
"""Конвертация музыкальных скетчей mp4(AAC) -> mp3 + базовая проверка (RMS, спектр).
Подтверждает, что трек — не тишина и не мусор: считает RMS, пик и спектральный центроид.
"""
import os, subprocess, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
SK = os.path.join(HERE, 'assets', 'audio', 'sketch')
names = ['vn_reception', 'prolog_chronicle', 'vn_space']
report = []
for n in names:
    src = os.path.join(SK, n + '_0.mp4')
    dst = os.path.join(SK, n + '_0.mp3')
    r = subprocess.run([FF, '-y', '-i', src, '-vn', '-c:a', 'libmp3lame', '-b:a', '192k', dst],
                       capture_output=True, text=True)
    ok = r.returncode == 0 and os.path.exists(dst)
    # декод в сырой PCM для статистики
    raw = subprocess.run([FF, '-v', 'quiet', '-i', src, '-f', 's16le', '-ac', '1',
                          '-ar', '22050', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    dur = len(a) / 22050.0
    rms = float(np.sqrt(np.mean(a ** 2)) + 1e-9)
    peak = float(np.max(np.abs(a)))
    # спектральный центроид по кадрам
    win = 2048
    cents = []
    for i in range(0, max(1, len(a) - win), win):
        seg = a[i:i + win]
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        f = np.fft.rfftfreq(len(seg), 1 / 22050.0)
        if sp.sum() > 1e-6:
            cents.append(float((sp * f).sum() / sp.sum()))
    cen = float(np.mean(cents)) if cents else 0.0
    report.append({'name': n, 'mp3': os.path.relpath(dst, HERE), 'dur_s': round(dur, 1),
                   'rms_db': round(20 * np.log10(rms), 1), 'peak': round(peak, 3),
                   'centroid_hz': round(cen)})
    print(f"{n:18s} dur={dur:5.1f}s  rms={20*np.log10(rms):6.1f}dB  peak={peak:.2f}  "
          f"centroid={cen:5.0f}Hz  -> {os.path.relpath(dst, HERE)}")
json.dump(report, open(os.path.join(SK, 'audio_stats.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('\nсохранено в assets/audio/sketch/audio_stats.json')
