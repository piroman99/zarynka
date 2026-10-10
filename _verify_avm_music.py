# -*- coding: utf-8 -*-
"""Проверка: в новом out/avm_v3_epic.mp4 звучит именно theme_epic_1 (а не _0).
Декодируем по 6 с аудио в моно 8 кГц PCM и сравниваем попарно (корреляция + MAE),
плюс рисуем волновые формы в assets/review/review_23_avm_music.png.
"""
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
SR, DUR = 8000, 6


def pcm(path, ss=0.0):
    r = subprocess.run([FF, "-v", "error", "-ss", str(ss), "-t", str(DUR), "-i", path,
                        "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32)
    if a.size == 0:
        raise RuntimeError(f"no audio from {path}: {r.stderr[-200:]}")
    return a


def corr(a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / (np.sqrt((a*a).sum() * (b*b).sum()) + 1e-9))


def mae(a, b):
    n = min(len(a), len(b))
    return float(np.abs(a[:n] - b[:n]).mean())


tr = {}
tr["epic_1.mp3"] = pcm(os.path.join(HERE, "assets/audio/theme_epic_1.mp3"))
tr["epic_0.mp3"] = pcm(os.path.join(HERE, "assets/audio/theme_epic_0.mp3"))
tr["avm NEW"] = pcm(os.path.join(HERE, "out/avm_v3_epic.mp4"))
tr["avm OLD(_0)"] = pcm(os.path.join(HERE, ".tmp_diag/avm_v3_epic_theme0.mp4"))
tr["avm 9x16"] = pcm(os.path.join(HERE, "out/avm_v3_epic_9x16.mp4"))

print(f"{'pairs':28s} {'corr':>7s} {'mae':>8s}")
for a in ("epic_1.mp3", "epic_0.mp3"):
    for b in ("avm NEW", "avm OLD(_0)", "avm 9x16"):
        print(f"{a:12s} vs {b:12s} {corr(tr[a], tr[b]):7.3f} {mae(tr[a], tr[b]):8.1f}")

# лист волновых форм
Wv, Hv = 900, 130
names = ["epic_0.mp3", "epic_1.mp3", "avm NEW", "avm OLD(_0)"]
sheet = Image.new("RGB", (Wv + 20, (Hv + 34) * len(names) + 10), (18, 20, 26))
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
except Exception:
    f = ImageFont.load_default()
for i, nm in enumerate(names):
    y0 = 10 + i * (Hv + 34)
    d.text((10, y0), nm, fill=(235, 232, 226), font=f)
    a = tr[nm][:SR * DUR]
    step = max(1, len(a) // Wv)
    col = (60, 200, 120) if "1" in nm or "NEW" in nm else (230, 120, 90)
    for x in range(Wv):
        seg = a[x * step:(x + 1) * step]
        if seg.size == 0:
            break
        lo, hi = float(seg.min()), float(seg.max())
        yy = y0 + 26 + Hv / 2
        d.line([(10 + x, yy - hi / 32768 * Hv / 2), (10 + x, yy - lo / 32768 * Hv / 2)], fill=col)
    d.line([(10, y0 + 26 + Hv / 2), (10 + Wv, y0 + 26 + Hv / 2)], fill=(90, 95, 105))
out = os.path.join(HERE, "assets/review/review_23_avm_music.png")
sheet.save(out)
print("saved", os.path.relpath(out, HERE), sheet.size)
