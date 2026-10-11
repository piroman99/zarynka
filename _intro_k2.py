# -*- coding: utf-8 -*-
"""Интро «Зарянки», концепт К2 — ЗНАЧОК-ИЛЛЮМИНАТОР с ПЕРЕВОРОТОМ (черновик, локально, 0 ₽).

Сцена: золотой пятиугольный значок (лицо — лого B с птицей вправо).
1.0–2.2 с  значок переворачивается на ребре (3D-флип вокруг вертикальной оси);
           на ОБОРОТЕ — не птица, а круглый ИЛЛЮМИНАТОР: окно в звёздное небо.
2.2–2.8 с  обод иллюминатора «становится ободом шлема».
2.8–4.2 с  зум внутрь: проваливаемся сквозь стекло → звёзды с параллаксом → растёт Марс.
4.2–5.6 с  титул «ЗАРЯНКА».

Выход: out/intro_k2_draft.mp4 (1920×1080, 25 fps, без звука).
Значок-оборот: assets/gen/znachek_k2_back.png
"""
import os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
LOGO = os.path.join(HERE, 'assets', 'gen', 'logo_b_0.jpg')
BIRDSRC = os.path.join(HERE, 'assets', 'orig', 'icon_large.png')
OUTDIR = os.path.join(HERE, '.tmp_intro_k2')
OUT = os.path.join(HERE, 'out', 'intro_k2_draft.mp4')
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


def ease(x):
    return x * x * (3 - 2 * x)


def smoothstep(a, b, x):
    if b == a:
        return 0.0 if x < a else 1.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


class Znachek:
    def __init__(self, size=1024, rot=-90):
        self.size = size
        self.rot = rot
        S = size
        cx = cy = S / 2
        self.cx, self.cy = cx, cy
        self.Rp = Rp = S * 0.49
        self.Rc = Rc = Rp * 0.68

        # ---------- ЛИЦО (лого B, птица вправо) ----------
        face = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(face)
        for r, col in [(Rp, GOLD_D), (Rp - 5, (176, 140, 66)), (Rp - 11, GOLD),
                       (Rp - 20, GOLD_L), (Rp - 30, GOLD), (Rp - 40, (196, 158, 82))]:
            d.polygon(pent(cx, cy, r, rot), fill=col)
        d.polygon(pent(cx, cy, Rp, rot), outline=(96, 72, 30, 255), width=3)
        d.ellipse([cx - Rc - 6, cy - Rc - 6, cx + Rc + 6, cy + Rc + 6], fill=GOLD_D)
        lg = Image.open(LOGO).convert('RGB')
        cx0, cy0, R0 = 511.5, 514.0, 391.0
        crop = lg.crop((int(cx0 - R0), int(cy0 - R0), int(cx0 + R0), int(cy0 + R0)))
        crop = crop.resize((int(Rc * 2), int(Rc * 2)), Image.LANCZOS).transpose(Image.FLIP_LEFT_RIGHT)
        m = Image.new('L', (int(Rc * 2), int(Rc * 2)), 0)
        ImageDraw.Draw(m).ellipse([0, 0, int(Rc * 2) - 1, int(Rc * 2) - 1], fill=255)
        crop = crop.convert('RGBA'); crop.putalpha(m)
        face.paste(crop, (int(cx - Rc), int(cy - Rc)), crop)
        d.ellipse([cx - Rc, cy - Rc, cx + Rc, cy + Rc], outline=GOLD_L, width=4)
        self.face = face

        # ---------- ОБОРОТ (иллюминатор: звёздное небо + Марс) ----------
        back = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(back)
        for r, col in [(Rp, GOLD_D), (Rp - 5, (176, 140, 66)), (Rp - 11, GOLD),
                       (Rp - 20, GOLD_L), (Rp - 30, GOLD), (Rp - 40, (196, 158, 82))]:
            d.polygon(pent(cx, cy, r, rot), fill=col)
        d.polygon(pent(cx, cy, Rp, rot), outline=(96, 72, 30, 255), width=3)
        # обод иллюминатора
        d.ellipse([cx - Rc - 10, cy - Rc - 10, cx + Rc + 10, cy + Rc + 10], fill=(120, 92, 44, 255))
        d.ellipse([cx - Rc - 4, cy - Rc - 4, cx + Rc + 4, cy + Rc + 4], fill=(196, 158, 82, 255))
        # стекло (космос)
        glass = Image.new('RGBA', (int(Rc * 2), int(Rc * 2)), (8, 10, 22, 255))
        gd = ImageDraw.Draw(glass)
        rng = np.random.default_rng(11)
        for _ in range(220):
            sx = rng.uniform(0, Rc * 2); sy = rng.uniform(0, Rc * 2)
            rr = rng.uniform(0.6, 2.0)
            gd.ellipse([sx - rr, sy - rr, sx + rr, sy + rr],
                       fill=(210, 216, 240, int(rng.uniform(90, 235))))
        # Марс в уголке
        mx, my, mr = Rc * 1.30, Rc * 1.28, Rc * 0.30
        gd.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(176, 78, 52, 255))
        gd.ellipse([mx - mr * 0.55, my - mr * 0.5, mx - mr * 0.1, my + mr * 0.1],
                   fill=(206, 110, 78, 255))
        m = Image.new('L', (int(Rc * 2), int(Rc * 2)), 0)
        ImageDraw.Draw(m).ellipse([0, 0, int(Rc * 2) - 1, int(Rc * 2) - 1], fill=255)
        glass = glass.convert('RGBA'); glass.putalpha(m)
        back.paste(glass, (int(cx - Rc), int(cy - Rc)), glass)
        d.ellipse([cx - Rc, cy - Rc, cx + Rc, cy + Rc], outline=(20, 24, 40, 255), width=6)
        d.ellipse([cx - Rc, cy - Rc, cx + Rc, cy + Rc], outline=GOLD_L, width=3)
        self.back = back

    def render_face(self, which, scale, persp_x):
        """Нарисовать значок с перспективным сжатием по X (persp_x = cos флипа)."""
        src = self.face if which == 'front' else self.back
        side = max(2, int(self.size * scale))
        im = src.resize((side, side), Image.LANCZOS)
        sx = max(0.02, abs(persp_x))
        im = im.resize((max(2, int(side * sx)), side), Image.LANCZOS)
        return im


ZN = Znachek()
ZN.face.save(os.path.join(GEN, 'znachek_k1.png'))
ZN.back.save(os.path.join(GEN, 'znachek_k2_back.png'))
print('значки сохранены')

# ---------- фон: градиент + звёзды (для сцены К2 — чуть глубже, фиолетово-синий) ----------
def radial_bg(w, h, col_out, col_in):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt((xx - w / 2) ** 2 + (yy - h / 2) ** 2) / (max(w, h) * 0.62)
    r = np.clip(r, 0, 1)
    out = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        out[:, :, i] = col_out[i] * r + col_in[i] * (1 - r)
    return Image.fromarray(out.astype(np.uint8), 'RGB')


BG = radial_bg(W, H, (5, 5, 14), (20, 18, 42))
rng = np.random.default_rng(7)
STARS = [(rng.integers(0, W), rng.integers(0, H), rng.uniform(0.6, 2.0), rng.uniform(0, 1))
         for _ in range(180)]


def render(f):
    t = f / FPS
    bg = BG.copy()
    bd = ImageDraw.Draw(bg)
    tw = smoothstep(0.0, 1.6, t)
    for (sx, sy, sr, ph) in STARS:
        al = int(95 * tw * (0.5 + 0.5 * math.sin(t * 2.4 + ph * 6.28)))
        bd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(215, 220, 240, max(0, al)))
    bg = bg.convert('RGBA')

    # ================= ФАЗА 1: флип значка (0 .. 2.6) =================
    if t < 2.85:
        if t < 1.0:
            sc = 0.97 + 0.035 * ease(t / 1.0)
            persp = 1.0
            glow = smoothstep(0.2, 1.0, t) * 0.30
        else:
            u = smoothstep(1.0, 2.2, t)
            theta = u * math.pi                 # 0 -> pi
            persp = math.cos(theta)
            sc = 1.005 + 0.02 * u
            glow = 0.30 + 0.55 * (1 - abs(persp))  # на ребре вспышка металла
        which = 'front' if persp >= 0 else 'back'
        im = ZN.render_face(which, sc * 0.62, persp)
        z = np.array(im).astype(np.float32)
        a = z[:, :, 3:4] / 255.0
        z[:, :, :3] = np.clip(z[:, :, :3] + glow * 80 * a, 0, 255)
        zn = Image.fromarray(np.clip(z, 0, 255).astype(np.uint8), 'RGBA')
        if glow > 0.05:
            big = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            big.paste(zn, (int(W / 2 - zn.width / 2), int(H / 2 - zn.height / 2)), zn)
            gl = big.filter(ImageFilter.GaussianBlur(24))
            ga = np.array(gl).astype(np.float32)
            ga[:, :, :3] = np.clip(ga[:, :, :3] * 1.4 + np.array([255, 205, 120]), 0, 255)
            ga[:, :, 3] *= min(1.0, glow * 1.0)
            bg = Image.alpha_composite(bg, Image.fromarray(ga.astype(np.uint8), 'RGBA'))
        zt = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        zt.paste(zn, (int(W / 2 - zn.width / 2), int(H / 2 - zn.height / 2)), zn)
        bg = Image.alpha_composite(bg, zt)

    # ================= ФАЗА 2: зум внутрь иллюминатора (2.6 .. 4.2) ==============
    if t >= 2.6:
        q = smoothstep(2.6, 4.2, t)
        # звёзды летят на зрителя (параллакс): растут из центра
        st = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        for k, (sx, sy, sr, ph) in enumerate(STARS):
            dx = (sx - W / 2); dy = (sy - H / 2)
            grow = 1.0 + q * 2.6
            x = W / 2 + dx * grow
            y = H / 2 + dy * grow
            if not (0 <= x < W and 0 <= y < H):
                continue
            rr = sr * (1 + q * 2.2)
            al = int(200 * min(1.0, q * 1.6))
            sd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(220, 226, 245, al))
        st = st.filter(ImageFilter.GaussianBlur(1))
        bg = Image.alpha_composite(bg, st)
        # Марс растёт
        mrp = (0.10 + 0.42 * ease(q)) * H
        mx, my = W * 0.5, H * 0.52
        mars = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        md = ImageDraw.Draw(mars)
        md.ellipse([mx - mrp, my - mrp, mx + mrp, my + mrp], fill=(178, 82, 54, 255))
        md.ellipse([mx - mrp * 0.62, my - mrp * 0.5, mx - mrp * 0.08, my + mrp * 0.16],
                   fill=(208, 116, 82, 255))
        md.ellipse([mx + mrp * 0.15, my - mrp * 0.35, mx + mrp * 0.55, my + mrp * 0.05],
                   fill=(160, 70, 46, 255))
        mars = mars.filter(ImageFilter.GaussianBlur(2))
        na = smoothstep(2.9, 3.7, t)
        ma = np.array(mars).astype(np.float32)
        ma[:, :, 3] *= na
        bg = Image.alpha_composite(bg, Image.fromarray(np.clip(ma, 0, 255).astype(np.uint8), 'RGBA'))
        # обод шлема-иллюминатора, уходящий за кадр
        if t < 3.6:
            ra = 1 - smoothstep(2.8, 3.6, t)
            rim = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            rdw = ImageDraw.Draw(rim)
            rr = ZN.Rc * 0.62 * (1 + q * 3.4)
            rdw.ellipse([W / 2 - rr, H / 2 - rr, W / 2 + rr, H / 2 + rr],
                        outline=(214, 176, 96, int(220 * ra)), width=max(2, int(10 * ra)))
            bg = Image.alpha_composite(bg, rim)

    # ---- титул ----
    if t > 4.15:
        ta = smoothstep(4.2, 5.0, t)
        dr = ImageDraw.Draw(bg)
        f1 = ImageFont.truetype(GOTHIC, 150)
        txt = 'З А Р Я Н К А'
        w1 = dr.textlength(txt, font=f1)
        yy = H / 2 - 70
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).text(((W - w1) / 2, yy), txt, font=f1, fill=(255, 210, 130, int(200 * ta)))
        gl = gl.filter(ImageFilter.GaussianBlur(16))
        bg = Image.alpha_composite(bg, gl)
        dr = ImageDraw.Draw(bg)
        dr.text(((W - w1) / 2, yy), txt, font=f1, fill=(248, 240, 225, int(255 * ta)))
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
print('ffmpeg rc', r.returncode, os.path.relpath(OUT, HERE),
      os.path.getsize(OUT) if os.path.exists(OUT) else 0)
if r.returncode:
    print(r.stderr[-1500:])

# контрольный лист (К2)
sheet = Image.new('RGB', (4 * 480 + 20 * 5, 2 * 270 + 20 * 3), (16, 16, 20))
i = 0
for tt in (0.4, 1.3, 2.0, 2.5, 3.0, 3.5, 4.6, 5.4):
    src = render(int(tt * FPS)).resize((480, 270), Image.LANCZOS)
    x = 20 + (i % 4) * (480 + 20); y = 20 + (i // 4) * (270 + 20)
    sheet.paste(src, (x, y))
    ImageDraw.Draw(sheet).text((x + 8, y + 6), '%.1f c' % tt,
                               font=ImageFont.truetype(LATO, 22), fill=(255, 220, 120))
    i += 1
sheet.save(os.path.join(REVIEW, 'review_32_intro_k2.png'))
print('лист: assets/review/review_32_intro_k2.png', sheet.size)
