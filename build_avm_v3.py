# -*- coding: utf-8 -*-
"""Интро-аниматик «Зарянки» v3 — с НАСТОЯЩИМ движением (image-to-video клипы).
Заказчик: «ничего интересного» -> добавляем живые клипы (корабль, станция, Екатерина
в скафандре), динамичный монтаж, титры. Всё локально (ffmpeg), денег не тратит.

Пропорции: каждый источник укладывается в 16:9 «contain» поверх тёмного
градиента с виньеткой (2026-10-17, вместо blur-pad — Иван: «полосы не смотрятся»).
Логотип — в круге (logo_b, вырезаем диск по альфе), приёмная — готовый 16:9
kate_reception_vn_0.png (комбинезон, канон).
"""
import os, glob, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TMP = os.path.join(HERE, ".tmp_intro3")
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
W, H, FPS = 1920, 1080, 25
TR = 0.5

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

# ------------------------------------------------------------------ тёмный фон (вместо blur-pad)
_BG_CACHE = os.path.join(TMP, "bg_dark_%dx%d.png" % (1920, 1080))

def bg_dark():
    """Тёмный холодный градиент с виньеткой — фон для вертикальных кадров."""
    if os.path.exists(_BG_CACHE):
        return _BG_CACHE
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W * 0.5, H * 0.46
    r = np.sqrt(((xx - cx) / (W * 0.62)) ** 2 + ((yy - cy) / (H * 0.72)) ** 2)
    r = np.clip(r, 0.0, 1.0) ** 1.35
    inner = np.array([30, 33, 41], np.float32)
    outer = np.array([7, 8, 11], np.float32)
    img = inner * (1 - r)[..., None] + outer * r[..., None]
    noise = np.random.default_rng(7).normal(0.0, 0.9, (H, W, 1))
    img = np.clip(img + noise, 0, 255).astype(np.uint8)
    Image.fromarray(img).save(_BG_CACHE)
    return _BG_CACHE

# ------------------------------------------------------------------ still -> 16:9 png
def _cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    return im.crop(((im.width - w) // 2, (im.height - h) // 2,
                    (im.width - w) // 2 + w, (im.height - h) // 2 + h))

def _contain(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)

def fit16_still(src):
    im = Image.open(src).convert("RGB")
    if abs(im.width / im.height - W / H) < 0.02:
        out = im.resize((W, H), Image.LANCZOS)
    else:
        bg = Image.open(bg_dark()).convert("RGB").copy()
        fg = _contain(im, W, H)
        bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
        out = bg
    p = os.path.join(TMP, "fit_" + os.path.basename(src).rsplit(".", 1)[0] + ".png")
    out.save(p)
    return p

# ------------------------------------------------------------------ логотип в круге
_LOGO_CACHE = {}

def logo_circle(name="logo_b_0.jpg", diam=460):
    """Квадрат логотипа -> RGBA-круг: вырезаем сам кремовый диск (с золотым кантом)."""
    key = (name, diam)
    if key in _LOGO_CACHE:
        return _LOGO_CACHE[key]
    src = os.path.join(HERE, "assets", "gen", name)
    if not os.path.exists(src):
        return None
    im = Image.open(src).convert("RGB")
    a = np.asarray(im)
    ys, xs = np.nonzero(a.min(axis=2) < 246)   # белое поле 255 -> кремовый диск
    cx, cy = (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0
    rad = min(xs.max() - xs.min(), ys.max() - ys.min()) / 2.0 - 1.5
    sz = int(round(rad * 2))
    sq = im.crop((round(cx - rad), round(cy - rad), round(cx - rad) + sz, round(cy - rad) + sz))
    S = 4                                     # суперсэмплинг маски — гладкий край
    m = Image.new("L", (sz * S, sz * S), 0)
    ImageDraw.Draw(m).ellipse((2 * S, 2 * S, sz * S - 2 * S, sz * S - 2 * S), fill=255)
    m = m.resize((sz, sz), Image.LANCZOS)
    rgba = sq.convert("RGBA")
    rgba.putalpha(m)
    rgba = rgba.resize((diam, diam), Image.LANCZOS)
    _LOGO_CACHE[key] = rgba
    return rgba

# ------------------------------------------------------------------ cards
def card(title, subtitle=None, logo="logo_b_0.jpg", tsize=118):
    im = Image.open(bg_dark()).convert("RGB").copy()
    d = ImageDraw.Draw(im)
    if logo:
        lg = logo_circle(logo, 460)
        if lg is not None:
            im.paste(lg, ((W - lg.width) // 2, 118), lg)
    f1, f2 = font(tsize), font(38)
    d.text(((W - d.textlength(title, font=f1)) / 2, 655), title, fill=(240, 238, 232), font=f1)
    if subtitle:
        d.text(((W - d.textlength(subtitle, font=f2)) / 2, 820), subtitle,
               fill=(190, 186, 176), font=f2)
    p = os.path.join(TMP, "card_" + title[:8] + ".png")
    im.save(p)
    return p

# ------------------------------------------------------------------ Ken Burns (still)
def kb(src, dst, secs, mode="in"):
    frames = max(2, int(secs * FPS))
    if mode == "in":
        z, x, y = "min(1+0.0013*on,1.16)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif mode == "out":
        z, x, y = "max(1.16-0.0013*on,1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif mode == "left":
        z, x, y = "1.15", f"(iw-iw/zoom)*(1-on/{frames})", "ih/2-(ih/zoom/2)"
    else:
        z, x, y = "1", "0", "0"
    vf = (f"scale={W*2}:{H*2},zoompan=z='{z}':d=1:x='{x}':y='{y}':s={W}x{H}:fps={FPS},"
          f"setsar=1,format=yuv420p")
    r = subprocess.run([FF, "-y", "-loop", "1", "-t", f"{secs:.3f}", "-i", src, "-vf", vf,
                        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", str(FPS), dst],
                       capture_output=True, text=True)
    if r.returncode:
        print("  kb err:", r.stderr[-260:])
    return r.returncode == 0

# ------------------------------------------------------------------ video -> 16:9 clip
def v_fit16(src, dst, secs):
    """Клип: тёмный градиент на весь кадр + сам клип целиком по центру (без искажений)."""
    vf = (
        f"[1:v]scale={W}:{H}:force_original_aspect_ratio=decrease[fgs];"
        f"[0:v][fgs]overlay=(W-w)/2:(H-h)/2:shortest=1,setsar=1,fps={FPS},"
        f"format=yuv420p[out]"
    )
    r = subprocess.run([FF, "-y", "-loop", "1", "-t", f"{secs:.3f}", "-i", bg_dark(),
                        "-i", src, "-filter_complex", vf, "-map", "[out]",
                        "-t", f"{secs:.3f}", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "19", "-r", str(FPS), dst], capture_output=True, text=True)
    if r.returncode:
        print("  vfit err:", r.stderr[-400:])
    return r.returncode == 0

# ------------------------------------------------------------------ shots
GEN = os.path.join(HERE, "assets", "gen")
VID = os.path.join(GEN, "vid")

shots = [
    ("still", card("ЗАРЯНКА"), 2.6, "in"),
    ("video", os.path.join(VID, "i2v_ship_0.mp4"), 5.4, None),
    ("still", os.path.join(GEN, "ok_space_station_0.jpg"), 3.2, "in"),
    ("video", os.path.join(VID, "i2v_station_0.mp4"), 5.2, None),
    ("still", os.path.join(GEN, "kate_reception_vn_0.png"), 3.6, "in"),
    ("video", os.path.join(VID, "i2v_kate_suit_0.mp4"), 5.2, None),
    ("still", os.path.join(GEN, "ok_x_kate_moon_0.jpg"), 4.0, "out"),
    ("still", card("Скоро", "по рассказу Александра «Котобус» Горбова"), 4.2, "in"),
]

clips = []
for i, (kind, src, secs, mode) in enumerate(shots):
    if not os.path.exists(src):
        print("  нет:", os.path.basename(src))
        continue
    dst = os.path.join(TMP, f"s_{i:02d}.mp4")
    ok = False
    if kind == "video":
        ok = v_fit16(src, dst, secs)
    else:
        ok = kb(fit16_still(src), dst, secs, mode)
    if ok:
        clips.append((dst, secs))
        print(f"  shot {i} ok ({kind}, {secs}s)")

# ------------------------------------------------------------------ xfade
joined = os.path.join(TMP, "joined.mp4")
if len(clips) == 1:
    subprocess.run([FF, "-y", "-i", clips[0][0], "-c", "copy", joined])
else:
    inputs = []
    for c, _ in clips:
        inputs += ["-i", c]
    fc, acc, last = [], clips[0][1], "[0:v]"
    for i in range(1, len(clips)):
        off = acc - TR
        out = f"[v{i}]"
        fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={TR}:offset={off:.3f}{out}")
        acc = off + clips[i][1]
        last = out
    r = subprocess.run([FF, "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", last,
                        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                        "-pix_fmt", "yuv420p", "-r", str(FPS), joined],
                       capture_output=True, text=True)
    if r.returncode:
        print("xfade err:", r.stderr[-500:])
        lst = os.path.join(TMP, "list.txt")
        with open(lst, "w") as f:
            for c, _ in clips:
                f.write(f"file '{c}'\n")
        subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined],
                       capture_output=True, text=True)

# ------------------------------------------------------------------ music
music = [m for m in sorted(glob.glob(os.path.join(HERE, "assets", "audio", "theme_*")))
         if m.lower().endswith((".mp3", ".wav", ".m4a", ".ogg"))]
final = os.path.join(OUT, "avm_v3.mp4")
if music:
    r = subprocess.run([FF, "-y", "-i", joined, "-i", music[0], "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-shortest",
                        "-map", "0:v:0", "-map", "1:a:0", final], capture_output=True, text=True)
    print("music:", os.path.relpath(music[0], HERE))
else:
    r = subprocess.run([FF, "-y", "-i", joined, "-c", "copy", final], capture_output=True, text=True)
    print("music: (нет)")
print("final:", os.path.relpath(final, HERE), "rc", r.returncode,
      "size", os.path.getsize(final) if os.path.exists(final) else 0)
