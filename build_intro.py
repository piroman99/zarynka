# -*- coding: utf-8 -*-
"""Собрать интро-аниматик «Зарянки» (v2).
Правки заказчика:
  • ПРОПОРЦИИ: раньше zoompan растягивал портретные кадры в 16:9 (круг → эллипс 2.37:1).
    Теперь каждый кадр сначала укладывается в 16:9 «contain» поверх размытой копии (blur-pad),
    поэтому пропорции сохраняются.
  • КОНТЕНТ: вместо процедурных заглушек космоса — сгенерированные корабль, лунная станция,
    Екатерина в скафандре; кадр приёмной — без английской таблички.
  • Динамика: разный Ken Burns (внутрь/наружу/панорама) + кроссфейды.
Всё локально (ffmpeg из imageio-ffmpeg). Ничего не тратит.
"""
import os, glob, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
    try:
        import sys
        sys.path.insert(0, "/home/ivan/.nanobot/workspace/.probe/.lib")
        import imageio_ffmpeg
        FF = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
FF = FF or shutil.which("ffmpeg")
print("ffmpeg:", FF)

W, H = 1920, 1080
FPS = 25


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


# ---------------------------------------------------------------- 16:9 fit
def _cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def _contain(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)


def fit16(src):
    """Кадр в 16:9 БЕЗ искажений: размытая копия на фон + исходник целиком по центру."""
    im = Image.open(src).convert("RGB")
    if abs(im.width / im.height - W / H) < 0.02:
        out = im.resize((W, H), Image.LANCZOS)
    else:
        bg = _cover(im, W, H).filter(ImageFilter.GaussianBlur(46))
        bg = Image.eval(bg, lambda v: int(v * 0.55))  # затемнить фон
        fg = _contain(im, W, H)
        bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
        out = bg
    p = os.path.join(TMP, "fit16_" + os.path.basename(src).rsplit(".", 1)[0] + ".png")
    out.save(p)
    return p


# ---------------------------------------------------------------- cards
def card(title, subtitle=None, logo=True, fg=(240, 238, 232)):
    im = Image.new("RGB", (W, H), (11, 13, 18))
    d = ImageDraw.Draw(im)
    if logo:
        lp = os.path.join(HERE, "assets", "gen", "logo_a_0.jpg")
        if os.path.exists(lp):
            lg = Image.open(lp).convert("RGB")
            lg = lg.resize((360, round(lg.height * 360 / lg.width)), Image.LANCZOS)
            im.paste(lg, ((W - lg.width) // 2, 210))
    f1 = font(120)
    tw = d.textlength(title, font=f1)
    d.text(((W - tw) / 2, 660), title, fill=fg, font=f1)
    if subtitle:
        f2 = font(38)
        sw = d.textlength(subtitle, font=f2)
        d.text(((W - sw) / 2, 820), subtitle, fill=(190, 186, 176), font=f2)
    p = os.path.join(TMP, "card_" + title[:10] + ".png")
    im.save(p)
    return p


# ---------------------------------------------------------------- Ken Burns
def kb(src, dst, secs, mode="in"):
    frames = max(2, int(secs * FPS))
    if mode == "in":
        z, x, y = "min(1+0.0013*on,1.16)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif mode == "out":
        z, x, y = "max(1.16-0.0013*on,1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif mode == "left":   # панорама справа налево
        z = "1.15"
        x, y = f"(iw-iw/zoom)*(1-on/{frames})", "ih/2-(ih/zoom/2)"
    elif mode == "right":
        z = "1.15"
        x, y = f"(iw-iw/zoom)*on/{frames}", "ih/2-(ih/zoom/2)"
    else:  # still
        z, x, y = "1.0", "0", "0"
    vf = (f"scale={W*2}:{H*2},zoompan=z='{z}':d=1:x='{x}':y='{y}':s={W}x{H}:fps={FPS},"
          f"setsar=1,format=yuv420p")
    cmd = [FF, "-y", "-loop", "1", "-t", f"{secs:.3f}", "-i", src, "-vf", vf,
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-r", str(FPS), dst]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("  ffmpeg err:", r.stderr[-300:])
    return r.returncode == 0


# ---------------------------------------------------------------- shots
shots = [
    (card("ЗАРЯНКА"), 3.6, "in"),
    (os.path.join(HERE, "assets/gen/ok_office_clean_0.jpg"), 3.4, "right"),   # пустой кабинет
    (os.path.join(HERE, "assets/gen/ok_reception_fix2_0.jpg"), 4.0, "in"),    # Екатерина в кабинете
    (os.path.join(HERE, "assets/gen/ok_space_ship_0.jpg"), 4.4, "left"),      # корабль
    (os.path.join(HERE, "assets/gen/ok_space_station_0.jpg"), 4.4, "in"),     # лунная станция
    (os.path.join(HERE, "assets/gen/ok_kate_suit_0.jpg"), 4.2, "out"),        # Екатерина в скафандре
    (card("Скоро", "по рассказу Александра «Котобус» Горбова"), 4.4, "in"),
]

clips = []
for i, (src, secs, mode) in enumerate(shots):
    if not os.path.exists(src):
        print("  нет кадра:", src)
        continue
    ready = fit16(src) if not src.startswith(TMP) else src
    dst = os.path.join(TMP, f"c_{i:02d}.mp4")
    if kb(ready, dst, secs, mode):
        clips.append((dst, secs))
        print(f"  clip {i} ok ({mode}, {secs}s)")

# ---------------------------------------------------------------- xfade
TR = 0.6
joined = os.path.join(TMP, "joined.mp4")
if len(clips) == 1:
    shutil.copy(clips[0][0], joined)
else:
    inputs = []
    for c, _ in clips:
        inputs += ["-i", c]
    fc = []
    acc = clips[0][1]
    last = "[0:v]"
    for i in range(1, len(clips)):
        off = acc - TR
        out = f"[v{i}]"
        fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={TR}:offset={off:.3f}{out}")
        acc = off + clips[i][1]
        last = out
    cmd = [FF, "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", last,
                                 "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
                                 "-pix_fmt", "yuv420p", "-r", str(FPS), joined]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("xfade err:", r.stderr[-500:])
        # фолбэк: обычная склейка
        lst = os.path.join(TMP, "list.txt")
        with open(lst, "w") as f:
            for c, _ in clips:
                f.write(f"file '{c}'\n")
        subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined],
                       capture_output=True, text=True)

# ---------------------------------------------------------------- музыка
music = sorted(glob.glob(os.path.join(HERE, "assets", "audio", "theme_warm_*.*"))) + \
        sorted(glob.glob(os.path.join(HERE, "assets", "audio", "theme_epic_*.*")))
music = [m for m in music if m.lower().endswith((".mp3", ".wav", ".m4a", ".ogg"))]
final = os.path.join(OUT, "intro_animatic.mp4")
if music:
    cmd = [FF, "-y", "-i", joined, "-i", music[0], "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
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
