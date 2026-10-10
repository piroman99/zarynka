# -*- coding: utf-8 -*-
"""Собрать интро-аниматик «Зарянки»: титры-карточки + Ken Burns по кадрам + музыка.
Всё локально (ffmpeg из imageio-ffmpeg). Ничего не тратит.
"""
import os, glob, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TMP = os.path.join(HERE, ".tmp_intro")
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

FF = None
for cand in (
    "/home/ivan/.nanobot/workspace/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2",
    "/home/ivan/.nanobot/workspace/.playwright-browsers/ffmpeg-1011/ffmpeg-linux",
):
    if os.path.exists(cand):
        FF = cand
        break
if not FF:
    import sys
    sys.path.insert(0, "/home/ivan/.nanobot/workspace/.probe/.lib")
    try:
        import imageio_ffmpeg
        FF = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
FF = FF or shutil.which("ffmpeg")
print("ffmpeg:", FF)


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


W, H = 1920, 1080


def card(title, subtitle=None, logo=True, fg=(240, 238, 232)):
    im = Image.new("RGB", (W, H), (11, 13, 18))
    d = ImageDraw.Draw(im)
    if logo:
        lp = os.path.join(HERE, "assets", "gen", "logo_a_0.jpg")
        if os.path.exists(lp):
            lg = Image.open(lp).convert("RGB")
            lg = lg.resize((360, round(lg.height * 360 / lg.width)), Image.LANCZOS)
            im.paste(lg, ((W - lg.width) // 2, 200))
    f1 = font(120)
    tw = d.textlength(title, font=f1)
    d.text(((W - tw) / 2, 640), title, fill=fg, font=f1)
    if subtitle:
        f2 = font(40)
        sw = d.textlength(subtitle, font=f2)
        d.text(((W - sw) / 2, 800), subtitle, fill=(190, 186, 176), font=f2)
    p = os.path.join(TMP, f"card_{title[:10]}.png")
    im.save(p)
    return p


def kb(src, dst, secs=4.0, zoom_in=True, fps=25):
    """Ken Burns: медленный зум/пан по статичному кадру."""
    z = "min(1+0.0009*on,1.18)" if zoom_in else "max(1.18-0.0009*on,1.0)"
    vf = (f"scale={W*2}:-2,zoompan=z='{z}':d=1:"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={fps},"
          f"setsar=1,format=yuv420p")
    cmd = [FF, "-y", "-loop", "1", "-t", str(secs), "-i", src, "-vf", vf,
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-r", str(fps), dst]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("  ffmpeg err:", r.stderr[-300:])
    return r.returncode == 0


# ---- кадры интро ----
shots = []
shots.append((card("ЗАРЯНКА"), 4.0, True))
for img, secs, zi in [
    ("assets/gen/fxseries_c1_enters_0.jpg", 4.0, True),
    ("assets/bg_space.png", 4.0, False),
    ("assets/gen/fxseries_c3_face_0.jpg", 4.0, True),
    ("assets/bg_luna.png", 4.0, False),
]:
    p = os.path.join(HERE, img)
    if os.path.exists(p):
        shots.append((p, secs, zi))
shots.append((card("Скоро", "по рассказу Александра «Котобус» Горбова"), 4.5, False))

clips = []
for i, (src, secs, zi) in enumerate(shots):
    dst = os.path.join(TMP, f"clip_{i:02d}.mp4")
    if kb(src, dst, secs, zi):
        clips.append(dst)
        print("  clip", i, "ok")

# ---- склейка ----
lst = os.path.join(TMP, "list.txt")
with open(lst, "w") as f:
    for c in clips:
        f.write(f"file '{c}'\n")
joined = os.path.join(TMP, "joined.mp4")
subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined],
               capture_output=True, text=True)

# ---- музыка ----
music = sorted(glob.glob(os.path.join(HERE, "assets", "audio", "theme_warm_*.*"))) + \
        sorted(glob.glob(os.path.join(HERE, "assets", "audio", "theme_epic_*.*")))
music = [m for m in music if m.lower().endswith((".mp3", ".wav", ".m4a", ".ogg"))]
final = os.path.join(OUT, "intro_animatic.mp4")
if music:
    cmd = [FF, "-y", "-i", joined, "-i", music[0], "-c:v", "copy", "-c:a", "aac",
           "-shortest", "-map", "0:v:0", "-map", "1:a:0", final]
else:
    cmd = [FF, "-y", "-i", joined, "-c", "copy", final]
r = subprocess.run(cmd, capture_output=True, text=True)
print("music:", os.path.relpath(music[0], HERE) if music else "(нет — немое)")
print("final:", os.path.relpath(final, HERE), "rc", r.returncode)
if r.returncode != 0:
    print(r.stderr[-400:])
if os.path.exists(final):
    print("size:", os.path.getsize(final), "bytes")
