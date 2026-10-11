# -*- coding: utf-8 -*-
"""Интро «Зарянки», концепт К1 (черновик-аниматик, локально, 0 ₽).

Сцена: пятиугольный ЗНАЧОК с вписанным круглым лого (птица вправо).
0.0–1.1 с  значок в темноте, «дыхание» (зум 0.98→1.03), слабый золотой контровой свет.
1.1–2.3 с  вспышка изнутри; птица бьёт крыльями внутри значка (масштаб-пульс).
2.3–4.0 с  птица срывается и улетает вправо-вверх, унося свет; металл значка
           рассыпается искрами и тает (эрозия + частицы).
4.0–5.6 с  искры гаснут → проявляется титул «ЗАРЯНКА».

Выход: out/intro_k1_draft.mp4 (1920×1080, 25 fps, без звука), значок assets/gen/znachek_k1.png.
"""
import os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')
FF = os.path.abspath(FF)
LOGO = os.path.join(HERE, 'assets', 'gen', 'logo_b_0.jpg')
BIRDSRC = os.path.join(HERE, 'assets', 'orig', 'icon_large.png')
OUTDIR = os.path.join(HERE, '.tmp_intro_k1')
OUT = os.path.join(HERE, 'out', 'intro_k1_draft.mp4')
GEN = os.path.join(HERE, 'assets', 'gen')
REVIEW = os.path.join(HERE, 'assets', 'review')

W, H, FPS, DUR = 1920, 1080, 25, 5.6
NF = int(FPS * DUR)
GOLD_D = (150, 116, 52)
GOLD = (214, 176, 96)
GOLD_L = (246, 226, 164)
CREAM = (250, 242, 220)
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'


def pent(cx, cy, R, rot=-90):
    return [(cx + R * math.cos(math.radians(rot + k * 72)),
             cy + R * math.sin(math.radians(rot + k * 72))) for k in range(5)]


# ---------------------------------------------------------------- значок (база)
def build_znachek(size=1024, flip=True):
    """Пятиугольная плита + вписанное круглое лого B."""
    S = size
    cx = cy = S / 2
    Rp = S * 0.49                 # внешний радиус пятиугольника
    Rc = Rp * 0.68                # радиус вписанного круга (<= 0.809*Rp) — меньше,
                                   # чтобы пятиугольная плита читалась

    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # золотая плита: концентрические пятиугольники
    steps = [(Rp, GOLD_D), (Rp - 5, (176, 140, 66)), (Rp - 11, GOLD),
             (Rp - 20, GOLD_L), (Rp - 30, GOLD), (Rp - 40, (196, 158, 82))]
    for r, col in steps:
        d.polygon(pent(cx, cy, r), fill=col)
    d.polygon(pent(cx, cy, Rp), outline=(96, 72, 30, 255), width=3)
    # вырез под круглое лого
    d.ellipse([cx - Rc - 6, cy - Rc - 6, cx + Rc + 6, cy + Rc + 6], fill=GOLD_D)

    # круглое лого
    lg = Image.open(LOGO).convert('RGB')
    cx0, cy0, R0 = 511.5, 514.0, 391.0
    crop = lg.crop((int(cx0 - R0), int(cy0 - R0), int(cx0 + R0), int(cy0 + R0)))
    crop = crop.resize((int(Rc * 2), int(Rc * 2)), Image.LANCZOS)
    if flip:
        crop = crop.transpose(Image.FLIP_LEFT_RIGHT)
    m = Image.new('L', (int(Rc * 2), int(Rc * 2)), 0)
    ImageDraw.Draw(m).ellipse([0, 0, int(Rc * 2) - 1, int(Rc * 2) - 1], fill=255)
    crop = crop.convert('RGBA')
    crop.putalpha(m)
    im.paste(crop, (int(cx - Rc), int(cy - Rc)), crop)
    # золотое кольцо вокруг круга
    d.ellipse([cx - Rc, cy - Rc, cx + Rc, cy + Rc], outline=GOLD_L, width=4)
    return im, cx, cy, Rp, Rc


ZN, ZCX, ZCY, ZRP, ZRC = build_znachek()
ZN.save(os.path.join(GEN, 'znachek_k1.png'))
ZNP = np.array(ZN).astype(np.float32)
print('значок: assets/gen/znachek_k1.png', ZN.size)

# ---------------------------------------------------------------- ассеты
def radial_bg(w, h, col_out, col_in):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2, h / 2
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (max(w, h) * 0.62)
    r = np.clip(r, 0, 1)
    out = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        out[:, :, i] = col_out[i] * r + col_in[i] * (1 - r)
    return Image.fromarray(out.astype(np.uint8), 'RGB')


BG = radial_bg(W, H, (6, 8, 16), (26, 30, 48))

# звёздная пыль
rng = np.random.default_rng(7)
stars = [(rng.integers(0, W), rng.integers(0, H), rng.uniform(0.6, 1.9),
          rng.uniform(0, 1)) for _ in range(160)]

# птица (2016) — уносит свет; сохраняем родные красно-золотые цвета (зарянка),
# только чуть подсвечиваем и добавляем световой контур
bird = Image.open(BIRDSRC).convert('RGBA')
bb = bird.split()[3].getbbox()
bird = bird.crop(bb)
arr = np.array(bird).astype(np.float32)
arr[:, :, :3] = np.clip(arr[:, :, :3] * 1.18 + 12, 0, 255)
BIRD = Image.fromarray(arr.astype(np.uint8), 'RGBA')
# световой контур: размытая копия под птицей
BIRD_GLOW = BIRD.copy()
BIRD_GLOW.save(os.path.join(REVIEW, '_bird_spr.png'))

# маска эрозии металла (фиксированный шум)
erosion = rng.random((ZN.size[1], ZN.size[0])).astype(np.float32)

# искры
sparks = []
for _ in range(420):
    a = rng.uniform(0, 2 * math.pi)
    rr = ZRC * (0.4 + 0.62 * math.sqrt(rng.uniform(0, 1)))
    x0 = ZCX + rr * math.cos(a)
    y0 = ZCY + rr * math.sin(a)
    t0 = 2.3 + rng.uniform(0, 1.5)
    vx = rng.uniform(-40, 40)
    vy = rng.uniform(-120, -40)
    life = rng.uniform(0.7, 1.6)
    sparks.append([x0, y0, t0, vx, vy, life, rng.uniform(1.2, 3.2)])


def ease(x):
    return x * x * (3 - 2 * x)


def smoothstep(a, b, x):
    if b == a:
        return 0.0 if x < a else 1.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def render(f):
    t = f / FPS
    # ---- фон ----
    bg = BG.copy()
    bd = ImageDraw.Draw(bg)
    tw = smoothstep(0.0, 2.0, t)
    for (sx, sy, sr, ph) in stars:
        al = int(90 * tw * (0.5 + 0.5 * math.sin(t * 2.4 + ph * 6.28)))
        bd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(210, 215, 235, max(0, al)))
    bg = bg.convert('RGBA')

    # ---- значок ----
    if t < 4.05:
        if t < 1.1:
            sc = 0.98 + 0.05 * ease(t / 1.1)
        elif t < 2.3:
            sc = 1.03 + 0.035 * ease((t - 1.1) / 1.2)
        else:
            sc = 1.065 + 0.05 * ease(smoothstep(2.3, 4.0, t))
        # свечение изнутри
        glow = smoothstep(0.3, 1.15, t) * 0.35
        if 1.05 < t < 1.7:
            glow += 0.85 * (1 - smoothstep(1.05, 1.7, t))
        glow = min(glow, 1.1)

        # пульс (крылья)
        pulse = 1.0
        if 1.1 < t < 2.35:
            pulse = 1.0 + 0.035 * math.sin((t - 1.1) * 26)
        sc *= pulse

        side = int(ZN.size[0] * sc * 0.62)
        zn = Image.fromarray(ZNP.astype(np.uint8), 'RGBA').resize((side, side), Image.LANCZOS)
        z = np.array(zn).astype(np.float32)

        # свечение по контуру/изнутри: добавляем золотой свет к непрозрачным пикселям
        a = z[:, :, 3:4] / 255.0
        z[:, :, :3] = np.clip(z[:, :, :3] + glow * 90 * a, 0, 255)

        # эрозия металла (растворение)
        if t > 2.35:
            p = smoothstep(2.35, 4.0, t)
            yy, xx = np.mgrid[0:z.shape[0], 0:z.shape[1]]
            er = erosion[(yy * ZN.size[1] // z.shape[0]).clip(0, ZN.size[1] - 1),
                         (xx * ZN.size[0] // z.shape[1]).clip(0, ZN.size[0] - 1)]
            keep = (er > p).astype(np.float32)
            z[:, :, 3] *= keep * (1 - 0.35 * p)
        zn = Image.fromarray(np.clip(z, 0, 255).astype(np.uint8), 'RGBA')

        # ореол свечения (полноразмерный)
        if glow > 0.05:
            big = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            big.paste(zn, (int(W / 2 - side / 2), int(H / 2 - side / 2)), zn)
            gl = big.filter(ImageFilter.GaussianBlur(22))
            ga = np.array(gl).astype(np.float32)
            ga[:, :, :3] = np.clip(ga[:, :, :3] * 1.5 + np.array([255, 205, 120]), 0, 255)
            ga[:, :, 3] *= min(1.0, glow * 1.1)
            bg = Image.alpha_composite(bg, Image.fromarray(ga.astype(np.uint8), 'RGBA'))

        ztile = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ztile.paste(zn, (int(W / 2 - side / 2), int(H / 2 - side / 2)), zn)
        bg = Image.alpha_composite(bg, ztile)

    # ---- птица улетает ----
    if 1.05 < t:
        if t < 2.35:
            bx, by = W / 2, H / 2
            bsc = 0.16
            rot = 0
            ba = smoothstep(1.05, 1.5, t)
        else:
            q = smoothstep(2.4, 4.05, t)
            bx = W / 2 + q * (W * 0.36)
            by = H / 2 - q * (H * 0.42)
            bsc = 0.17 + q * 0.17
            rot = -10 * q
            ba = 1 - smoothstep(3.4, 4.05, t) * 0.85
        bs = int(H * bsc)
        bimg = BIRD.resize((bs, max(1, int(bs * BIRD.height / BIRD.width))), Image.LANCZOS)
        if rot:
            bimg = bimg.rotate(rot, expand=True, resample=Image.BICUBIC)
        ba = max(0.0, min(1.0, ba))
        # шлейф света
        trail = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        td = ImageDraw.Draw(trail)
        for k in range(1, 9):
            qq = k / 9.0
            if t >= 2.4:
                q2 = smoothstep(2.4, 4.05, max(2.4, t - 0.10 * k))
                tx = W / 2 + q2 * (W * 0.36)
                ty = H / 2 - q2 * (H * 0.42)
                rr = int(20 * (1 - qq) + 4)
                td.ellipse([tx - rr, ty - rr, tx + rr, ty + rr],
                           fill=(255, 230, 170, int(120 * (1 - qq) * (ba > 0))))
        trail = trail.filter(ImageFilter.GaussianBlur(7))
        bg = Image.alpha_composite(bg, trail)
        # световое пятно вокруг птицы
        halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(halo).ellipse([bx - bs * 0.62, by - bs * 0.62, bx + bs * 0.62, by + bs * 0.62],
                                     fill=(255, 226, 160, int(58 * ba)))
        halo = halo.filter(ImageFilter.GaussianBlur(30))
        bg = Image.alpha_composite(bg, halo)
        # световая подложка под птицей
        if ba > 0.02:
            gws = max(1, int(bs * 1.12))
            gw = BIRD.resize((gws, max(1, int(gws * BIRD.height / BIRD.width))), Image.LANCZOS)
            ga = np.array(gw).astype(np.float32)
            ga[:, :, :3] = np.array([255, 234, 175], np.float32)
            ga[:, :, 3] *= 0.85
            gw = Image.fromarray(np.clip(ga, 0, 255).astype(np.uint8), 'RGBA')
            gw = gw.filter(ImageFilter.GaussianBlur(9))
            gt = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            gt.paste(gw, (int(bx - gw.width / 2), int(by - gw.height / 2)), gw)
            bg = Image.alpha_composite(bg, gt)
        bimg.putalpha(bimg.split()[3].point(lambda v: int(v * ba)))
        btile = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        btile.paste(bimg, (int(bx - bimg.width / 2), int(by - bimg.height / 2)), bimg)
        bg = Image.alpha_composite(bg, btile)
    # ---- искры ----
    sp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sp)
    for (x0, y0, t0, vx, vy, life, size) in sparks:
        if t < t0 or t > t0 + life:
            continue
        u = (t - t0) / life
        x = x0 + vx * u * 0.6
        y = y0 + vy * u * 0.6 + 40 * u * u
        al = int(255 * (1 - u) ** 1.4)
        r = size * (1 - 0.4 * u)
        sd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 226, 160, max(0, al)))
    sp = sp.filter(ImageFilter.GaussianBlur(2))
    bg = Image.alpha_composite(bg, sp)

    # ---- вспышка ----
    if 1.02 < t < 1.6:
        fa = 0.55 * (1 - smoothstep(1.02, 1.6, t))
        fl = Image.new('RGBA', (W, H), (255, 240, 210, int(255 * fa)))
        bg = Image.alpha_composite(bg, fl)

    # ---- титул ----
    if t > 4.0:
        ta = smoothstep(4.05, 4.9, t)
        dr = ImageDraw.Draw(bg)
        f1 = ImageFont.truetype(GOTHIC, 150)
        txt = 'З А Р Я Н К А'
        w1 = dr.textlength(txt, font=f1)
        yy = H / 2 - 70
        # лёгкое свечение титула
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).text(((W - w1) / 2, yy), txt, font=f1, fill=(255, 210, 130, int(200 * ta)))
        gl = gl.filter(ImageFilter.GaussianBlur(16))
        bg = Image.alpha_composite(bg, gl)
        dr = ImageDraw.Draw(bg)
        dr.text(((W - w1) / 2, yy), txt, font=f1, fill=(248, 240, 225, int(255 * ta)))
        # линия
        lw = int(w1 * 0.5)
        dr.line([(W / 2 - lw / 2, yy + 175), (W / 2 + lw / 2, yy + 175)],
                fill=(214, 176, 96, int(230 * ta)), width=3)
        f2 = ImageFont.truetype(LATO, 40)
        sub = 'визуальная новелла по рассказу Александра Горбова'
        w2 = dr.textlength(sub, font=f2)
        dr.text(((W - w2) / 2, yy + 205), sub, font=f2, fill=(210, 205, 195, int(230 * ta)))

    return bg.convert('RGB')


os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
for f in range(NF):
    render(f).save(os.path.join(OUTDIR, 'f%04d.png' % f))
print('кадров:', NF)

r = subprocess.run([FF, '-y', '-framerate', str(FPS), '-i', os.path.join(OUTDIR, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', OUT],
                   capture_output=True, text=True)
print('ffmpeg rc', r.returncode, os.path.relpath(OUT, HERE), os.path.getsize(OUT) if os.path.exists(OUT) else 0)
if r.returncode:
    print(r.stderr[-1500:])

# контрольный лист
for name, idx in (('review_31', None),):
    pass
sheet = Image.new('RGB', (4 * 480 + 20 * 5, 2 * 270 + 20 * 3), (16, 16, 20))
i = 0
for tt in (0.4, 1.3, 2.0, 2.7, 3.2, 3.8, 4.6, 5.4):
    src = render(int(tt * FPS)).resize((480, 270), Image.LANCZOS)
    x = 20 + (i % 4) * (480 + 20)
    y = 20 + (i // 4) * (270 + 20)
    sheet.paste(src, (x, y))
    d = ImageDraw.Draw(sheet)
    d.text((x + 8, y + 6), '%.1f c' % tt, font=ImageFont.truetype(LATO, 22), fill=(255, 220, 120))
    i += 1
sheet.save(os.path.join(REVIEW, 'review_31_intro_k1.png'))
print('лист: assets/review/review_31_intro_k1.png', sheet.size)
