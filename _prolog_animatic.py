# -*- coding: utf-8 -*-
"""ЧЕРНОВИК-АНИМАТИК ПРОЛОГА «Зарянка» v4 (слои + появление по фразе + грейд + хвост).
P0 (3D-значок) + S1..S6 (с закадром) + S7 «проходная·очередь» (ХВОСТ БЕЗ РЕЧИ).
Оверлеи проявляются ПО ФРАЗЕ закадра («МАРС — ДЕЛО ОБЩЕЕ» и т.д. — в момент произнесения).
Голос: vo_prolog2 (Charon) + atempo 0.95. Грейд «тёплый архив»-lite.
Финал: речь кончается на S6, ДАЛЬШЕ идёт молчаливый S7, и только ПОСЛЕ него — затемнение
(правка заказчика 2026-10-11: «сначала закончим речь, потом затемнение»).
Выход: out/prolog_animatic_draft.mp4 (с голосом) и out/prolog_animatic_subs.mp4.
1920x1080, 25 fps.
"""
import os, sys, wave, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
MOCK = os.path.join(HERE, 'assets', 'mock', 'prolog')
VO = os.path.join(HERE, 'assets', 'audio', 'vo_prolog2')
BED = os.path.join(HERE, 'assets', 'audio', 'sketch', 'prolog_bed_soft_0.mp3')
TMP = os.path.join(HERE, '.tmp_animatic')
OUT_VO = os.path.join(HERE, 'out', 'prolog_animatic_draft.mp4')
OUT_SUB = os.path.join(HERE, 'out', 'prolog_animatic_subs.mp4')
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

W, H, FPS = 1920, 1080, 25
SW, SH = 2400, 1350
CF = 0.4                 # кроссфейд между кадрами, с
P0_SEC = 6.0
VO_TEMPO = 0.95
BED_VOL = 0.30
BED_VOL_SUB = 0.55
CREAM = (246, 238, 222)
REVEAL_FADE = 0.7        # длительность проявления оверлея, с
END_FADE = 2.4           # финальное затемнение, с
TAIL_SHOT = 's7'         # кадр-хвост «проходная·очередь» (БЕЗ закадра) — речь кончается перед ним
TAIL_SEC = 10.4          # длительность хвоста, с (последние END_FADE — затемнение)
GRADE = True             # грейд «тёплый архив»-lite (подтверждён заказчиком 2026-10-11)

sys.path.insert(0, HERE)
from prolog_script import SEG

# какие оверлеи кадра проявляются на какой фразе закадра
REVEALS = {
    's1': [('poster', 'Марс — дело общее')],
    's3': [('q1', 'Марс — дело общее'), ('q2', 'Общее!'), ('q3', 'обычных людей')],
    's4': [('video', 'слепил видеоролик'), ('q', 'неудобным вопросом')],
    's5': [('posters', 'лозунг'), ('soviet', 'Верховного Совета'), ('seats', 'два места')],
}

# ---- рендер значка (3D) -----------------------------------------------
_src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
_ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(_src, '_znak3d.py', 'exec'), _ns)
render3d = _ns['render']


def ease(x):
    return x * x * (3 - 2 * x)


def eio(x):
    return 4 * x**3 if x < 0.5 else 1 - (-2 * x + 2)**3 / 2


def angle_at(t):
    """Ребро — МЕЛЬКОМ: без паузы на 90°, сплошной проход (правка заказчика 2026-10-11)."""
    if t < 0.6:
        return 0.0
    if t < 2.30:
        return 180.0 * eio((t - 0.6) / 1.70)
    return 180.0


_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.clip(np.sqrt((_xx - W / 2) ** 2 + (_yy - H / 2) ** 2) / (W * 0.62), 0, 1)
_bgbuf = np.zeros((H, W, 3), np.float32)
for _i, (_co, _ci) in enumerate(zip((5, 5, 14), (20, 18, 42))):
    _bgbuf[:, :, _i] = _co * _r + _ci * (1 - _r)
BG = Image.fromarray(_bgbuf.astype(np.uint8), 'RGB')


# ---- грейд «тёплый архив»-lite ---------------------------------------
_CM = np.array([[0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]], np.float32)


def grade(im):
    """45% сепии + тёплый тинт + чуть контраста (НЕ гасит красные плакаты/золото значка)."""
    a = np.asarray(im, np.float32)
    s = np.clip(a @ _CM.T, 0, 255)
    b = 0.45 * s + 0.55 * a
    b[..., 0] = np.clip(b[..., 0] * 1.035, 0, 255)
    b[..., 1] = np.clip(b[..., 1] * 1.005, 0, 255)
    b[..., 2] = np.clip(b[..., 2] * 0.930, 0, 255)
    b = np.clip((b - 128.0) * 1.07 + 128.0, 0, 255)
    return Image.fromarray(b.astype(np.uint8), 'RGB')


def render_p0(t):
    t = max(0.0, min(P0_SEC, t))
    a = angle_at(t)
    zn = render3d(a, w=1920, h=1920)
    zn = zn.crop((0, 420, 1920, 1500))
    im = Image.alpha_composite(BG.convert('RGBA'), zn.convert('RGBA')).convert('RGB')
    if t > 5.2:
        im = Image.blend(im, Image.new('RGB', (W, H), (255, 255, 255)), ease(min(1.0, (t - 5.2) / 0.75)))
    return im


# ---- base + оверлеи ----------------------------------------------------
MOT = {
    's1': (0.96, 0.85, 0.50, 0.45, 0.50, 0.50),
    's2': (1.00, 0.90, 0.50, 0.55, 0.55, 0.50),
    's3': (0.94, 0.84, 0.50, 0.50, 0.50, 0.55),
    's4': (1.00, 0.90, 0.50, 0.50, 0.50, 0.50),
    's5': (0.90, 1.00, 0.50, 0.50, 0.52, 0.48),
    's6': (1.00, 0.87, 0.50, 0.42, 0.56, 0.50),
    's7': (1.00, 0.88, 0.50, 0.60, 0.54, 0.50),   # хвост: медленный наезд к будке с плакатом
}
_SRC = {n: Image.open(os.path.join(MOCK, n + '_base.png')).convert('RGB') for n in MOT}
OVL = {}   # name -> list of (rgb, alphaL, reveal_time)
for n, revs in REVEALS.items():
    lst = []
    for label, phrase in revs:
        p = os.path.join(MOCK, '%s_%s.png' % (n, label))
        if not os.path.exists(p):
            print('!! нет оверлея', p); continue
        ov = Image.open(p).convert('RGBA')
        lst.append((ov.convert('RGB'), ov.getchannel('A'), phrase))
    OVL[n] = lst


def crop_box(name, p):
    z0, z1, cx0, cx1, cy0, cy1 = MOT[name]
    z = z0 + (z1 - z0) * p
    cx = (cx0 + (cx1 - cx0) * p) * SW
    cy = (cy0 + (cy1 - cy0) * p) * SH
    cw = SW * z
    ch = cw * SH / SW
    x0 = min(max(cx - cw / 2, 0), SW - cw)
    y0 = min(max(cy - ch / 2, 0), SH - ch)
    return (int(x0), int(y0), int(x0 + cw), int(y0 + ch))


def render_mock(name, lt, dur):
    p = max(0.0, min(1.0, lt / dur if dur > 0 else 0))
    full = _SRC[name].copy()
    for rgb, alpha, phrase in OVL.get(name, []):
        rt = REVEAL_T.get((name, phrase))
        if rt is None:
            continue
        a = (lt - rt) / REVEAL_FADE
        a = 0 if a <= 0 else (1 if a >= 1 else ease(a))
        if a > 0.001:
            m = alpha if a >= 0.999 else alpha.point(lambda v, aa=a: int(v * aa))
            full.paste(rgb, (0, 0), m)
    box = crop_box(name, p)
    return full.crop(box).resize((W, H), Image.BILINEAR)


# ---- субтитры (текст-буквы, печатная машинка) --------------------------
_FT = ImageFont.truetype(LATO_B, 44)
MX, TOP = 300, 880
MAXW = W - 2 * MX


def wrap(text):
    words, lines, cur = text.split(' '), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if _FT.getlength(t) <= MAXW:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


LINES = {name: wrap(txt) for _, txt, name in SEG}


def draw_subs(im, name, p):
    lines = LINES[name]
    total = sum(len(l) for l in lines)
    n = int(max(0.0, min(1.0, p)) * total)
    band = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, 848, W, H], fill=(0, 0, 0, 120))
    im.paste(Image.alpha_composite(im.convert('RGBA'), band).convert('RGB'), (0, 0))
    d = ImageDraw.Draw(im, 'RGBA')
    y = TOTAL_TOP = TOP - 26
    used = 0
    for ln in lines:
        vis = ln[:max(0, n - used)]
        used += len(ln)
        if vis:
            d.text((MX, y), vis, font=_FT, fill=CREAM)
        y += 56


# ---- таймлайн ----------------------------------------------------------
def wdur(p):
    with wave.open(p, 'rb') as w:
        return w.getnframes() / float(w.getframerate())


os.makedirs(TMP, exist_ok=True)
VOSLOW = os.path.join(TMP, 'vo_slow')
os.makedirs(VOSLOW, exist_ok=True)

order = [name for _, _, name in SEG]
TXT = {name: txt for _, txt, name in SEG}
durs = {}
for name in order:
    src = os.path.join(VO, name + '_0.wav')
    dst = os.path.join(VOSLOW, name + '.wav')
    r = subprocess.run([FF, '-y', '-i', src, '-filter:a', 'atempo=%.3f' % VO_TEMPO,
                        '-ar', '48000', '-ac', '2', dst], capture_output=True, text=True)
    if r.returncode:
        print('atempo FAIL', name, r.stderr[-400:]); sys.exit(1)
    durs[name] = wdur(dst)

segs = [('P0', 0.0, P0_SEC)]
st = P0_SEC
for name in order:
    segs.append((name, st, durs[name]))
    st += durs[name]
VO_END = st               # здесь кончается закадровая речь
segs.append((TAIL_SHOT, VO_END, TAIL_SEC))   # молчаливый хвост S7
st += TAIL_SEC
TOTAL = st
NF = int(round(TOTAL * FPS))

# времена появления оверлеев (оценка по доле символов в озвучке сегмента)
REVEAL_T = {}
print('кадры:', NF, '| длительность %.1f c (%.2f мин)' % (TOTAL, TOTAL / 60))
for nm, a, dd in segs:
    print('  %-3s %6.2f -> %6.2f (%.2f c)' % (nm, a, a + dd, dd))
    if nm not in TXT:
        continue
    txt = TXT[nm]
    for label, phrase in REVEALS.get(nm, []):
        idx = txt.find(phrase)
        if idx < 0:
            idx = 0
        rt = idx / max(1, len(txt)) * dd
        REVEAL_T[(nm, phrase)] = rt
        print('        появление %-8s «%s» -> +%.2f c' % (label, phrase, rt))


def shot_at(t):
    for i in range(len(segs) - 1, -1, -1):
        nm, a, dd = segs[i]
        if t >= a - 1e-9:
            return i, nm, min(t - a, dd - 1e-6), dd
    return 0, segs[0][0], 0.0, segs[0][2]


def render_shot(nm, lt, dur):
    if nm == 'P0':
        return render_p0(lt)
    return render_mock(nm, lt, dur)


random.seed(3)
NOISE = Image.effect_noise((W + 240, H + 240), 14).convert('RGB')
BLACK = Image.new('RGB', (W, H), (0, 0, 0))


def grain(im):
    ox, oy = random.randint(0, 220), random.randint(0, 220)
    return Image.blend(im, NOISE.crop((ox, oy, ox + W, oy + H)), 0.05)


# ---- 1) немое видео ----------------------------------------------------
SILENT = os.path.join(TMP, 'prolog_silent.mp4')
os.makedirs(os.path.dirname(OUT_VO), exist_ok=True)
vcmd = [FF, '-y', '-nostats', '-loglevel', 'error',
        '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', '%dx%d' % (W, H),
        '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
        '-crf', '20', '-pix_fmt', 'yuv420p', SILENT]
# ВАЖНО: stderr НЕ в PIPE — иначе буфер трубы переполняется и ffmpeg встаёт (дедлок).
FFLOG = os.path.join(TMP, 'ffmpeg_silent.log')
_fflog = open(FFLOG, 'wb')
proc = subprocess.Popen(vcmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=_fflog)
for fidx in range(NF):
    t = fidx / FPS
    k, nm, lt, dur = shot_at(t)
    im = render_shot(nm, lt, dur)
    if k > 0 and (t - segs[k][1]) < CF:
        a = (t - segs[k][1]) / CF
        pnm, pa, pd = segs[k - 1]
        prev = render_shot(pnm, min(t - pa, pd - 1e-6), pd)
        im = Image.blend(prev, im, a)
    if GRADE:
        im = grade(im)
    if nm in TXT:
        draw_subs(im, nm, lt / dur if dur > 0 else 0)
    im = grain(im)
    # финальное затемнение в чёрное
    if t > TOTAL - END_FADE:
        f = max(0.0, min(1.0, (TOTAL - t) / END_FADE))
        im = Image.blend(BLACK, im, ease(f))
    proc.stdin.write(im.tobytes())
    if fidx % 200 == 0:
        print('  frame', fidx, '/', NF)
proc.stdin.close()
rc = proc.wait()
print('silent video rc', rc, os.path.getsize(SILENT) if os.path.exists(SILENT) else 0)
if rc:
    _fflog.flush()
    print(open(FFLOG).read()[-1500:]); sys.exit(1)

# ---- 2) звук -----------------------------------------------------------
AUD_VO = os.path.join(TMP, 'prolog_audio_vo.wav')
AUD_SUB = os.path.join(TMP, 'prolog_audio_subs.wav')
bed_out = TOTAL - 3.0
fc = ["[0:a]volume=%s,afade=t=in:st=0:d=1.5,afade=t=out:st=%.2f:d=3[bed]" % (BED_VOL, bed_out)]
vo_segs = [s for s in segs if s[0] in durs]     # только сегменты с озвучкой (без S7-хвоста)
for i, (nm, a, dd) in enumerate(vo_segs, start=1):
    fc.append("[%d:a]adelay=%d:all=1[v%d]" % (i, int(a * 1000), i))
mixin = "[bed]" + "".join("[v%d]" % i for i in range(1, len(vo_segs) + 1))
fc.append("%samix=inputs=%d:normalize=0,alimiter=level_in=1:limit=0.97[a]" % (mixin, len(vo_segs) + 1))
cmd = [FF, '-y', '-i', BED]
for nm, a, dd in vo_segs:
    cmd += ['-i', os.path.join(VOSLOW, nm + '.wav')]
cmd += ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', '%.3f' % TOTAL,
        '-ar', '48000', '-ac', '2', AUD_VO]
r = subprocess.run(cmd, capture_output=True, text=True)
print('audio VO rc', r.returncode)
if r.returncode:
    print(r.stderr[-1500:]); sys.exit(1)
r = subprocess.run([FF, '-y', '-i', BED, '-filter:a',
                    "volume=%s,afade=t=in:st=0:d=1.5,afade=t=out:st=%.2f:d=4,atrim=0:%.3f" % (BED_VOL_SUB, TOTAL - 4.0, TOTAL),
                    '-t', '%.3f' % TOTAL, '-ar', '48000', '-ac', '2', AUD_SUB], capture_output=True, text=True)
print('audio SUB rc', r.returncode)

# ---- 3) мультиплекс ----------------------------------------------------
for aud, out, tag in ((AUD_VO, OUT_VO, 'ГС'), (AUD_SUB, OUT_SUB, 'ПС')):
    r = subprocess.run([FF, '-y', '-i', SILENT, '-i', aud, '-c:v', 'copy', '-c:a', 'aac',
                        '-b:a', '192k', '-shortest', out], capture_output=True, text=True)
    print('[%s] rc=%d -> %s  %d bytes' % (tag, r.returncode, os.path.relpath(out, HERE),
                                          os.path.getsize(out) if os.path.exists(out) else 0))
    if r.returncode:
        print(r.stderr[-1000:])
