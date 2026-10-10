# -*- coding: utf-8 -*-
"""Пересобрать AVM v3 (epic) на выбранной музыке → 16:9 + 9:16.
Трек задаётся аргументом (по умолчанию assets/audio/theme_epic_1.mp3).
Видео берём из .tmp_intro3/joined.mp4 (немой, 29.92 с), звук — выбранный mp3.
"""
import os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

music = sys.argv[1] if len(sys.argv) > 1 else "assets/audio/theme_epic_1.mp3"
music = os.path.join(HERE, music) if not os.path.isabs(music) else music
joined = os.path.join(HERE, ".tmp_intro3", "joined.mp4")
out16 = os.path.join(HERE, "out", "avm_v3_epic.mp4")
out09 = os.path.join(HERE, "out", "avm_v3_epic_9x16.mp4")

print("music :", os.path.relpath(music, HERE), os.path.getsize(music), "B")
print("video :", os.path.relpath(joined, HERE))
assert os.path.exists(music) and os.path.exists(joined)

# бэкап прежних версий (в .tmp — не в git)
bakdir = os.path.join(HERE, ".tmp_avm_bak")
os.makedirs(bakdir, exist_ok=True)
for src in (out16, out09):
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(bakdir, os.path.basename(src)))
print("backups ->", os.path.relpath(bakdir, HERE))

# 16:9 — видео копируется, аудио — выбранный трек
r = subprocess.run([FF, "-y", "-i", joined, "-i", music,
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out16],
                   capture_output=True, text=True)
print("16:9 rc", r.returncode, os.path.getsize(out16) if os.path.exists(out16) else 0)
if r.returncode:
    print(r.stderr[-800:]); sys.exit(1)

# 9:16 — пересобрать из свежего 16:9 (blur-pad contain, звук копируется)
vf = (
    "split=2[bg][fg];"
    "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=48:2,eq=brightness=-0.22[bgb];"
    "[fg]scale=1080:1920:force_original_aspect_ratio=decrease[fgs];"
    "[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=25,format=yuv420p[out]"
)
r = subprocess.run([FF, "-y", "-i", out16, "-filter_complex", vf, "-map", "[out]", "-map", "0:a?",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "copy", "-r", "25", out09],
                   capture_output=True, text=True)
print("9:16 rc", r.returncode, os.path.getsize(out09) if os.path.exists(out09) else 0)
if r.returncode:
    print(r.stderr[-800:]); sys.exit(1)

for p in (out16, out09):
    info = subprocess.run([FF, "-hide_banner", "-i", p], capture_output=True, text=True).stderr
    print([l.strip() for l in info.splitlines() if "Duration" in l or "Stream" in l])
