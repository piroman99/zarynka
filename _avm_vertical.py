# -*- coding: utf-8 -*-
"""Вертикальная (9:16) версия эпичного тизера для «ВК Клипов».
Ничего не обрезаем: 16:9-кадр целиком «contain» по центру, фон — размытая копия (blur-pad).
Вход: out/avm_v3_epic.mp4  ->  Выход: out/avm_v3_epic_9x16.mp4 (1080x1920).
"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
W, H, FPS = 1080, 1920, 25
src = os.path.join(HERE, "out", "avm_v3_epic.mp4")
dst = os.path.join(HERE, "out", "avm_v3_epic_9x16.mp4")

vf = (
    f"split=2[bg][fg];"
    f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
    f"boxblur=48:2,eq=brightness=-0.22[bgb];"
    f"[fg]scale={W}:{H}:force_original_aspect_ratio=decrease[fgs];"
    f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={FPS},format=yuv420p[out]"
)
r = subprocess.run([FF, "-y", "-i", src, "-filter_complex", vf, "-map", "[out]",
                    "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "192k", "-r", str(FPS), dst],
                   capture_output=True, text=True)
print("rc", r.returncode, dst if os.path.exists(dst) else "", os.path.getsize(dst) if os.path.exists(dst) else 0)
if r.returncode:
    print(r.stderr[-600:])
# контрольный кадр
subprocess.run([FF, "-y", "-ss", "2.0", "-i", dst, "-frames:v", "1",
                "-vf", "scale=480:-1", os.path.join(HERE, "out", "_vert_check.png")], capture_output=True)
info = subprocess.run([FF, "-hide_banner", "-i", dst], capture_output=True, text=True).stderr
print([l.strip() for l in info.splitlines() if "Duration" in l or "Stream" in l])
