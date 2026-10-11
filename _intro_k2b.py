# -*- coding: utf-8 -*-
"""Интро «Зарянки», К2-УСЛОЖНЁННЫЙ — значок-призма с ВИДИМЫМ РЕБРОМ и ГРАВИРОВКОЙ.

Отличие от intro_k2_draft: значок — не плоская картинка с флипом по X, а
пятиугольная ПРИЗМА (лицо ↔ оборот, между ними металлическое РЕБРО-торец).
Движение: замах → быстрый флип (ребро мелькает) → ЗАМЕДЛЕНИЕ и ПАУЗА точно на
ребре (камера смотрит в торец, читается гравировка) → докрут → оборот-иллюминатор
→ зум внутрь → титул.

Гравировка на ребре задаётся RIB_TEXT (по умолчанию — выбор заказчика A).
Выход: out/intro_k2b_draft.mp4 (1920×1080, 25 fps, без звука).
Запуск: python3 _intro_k2b.py            (полная сборка)
        python3 _intro_k2b.py --sheet    (только контрольные кадры)
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.path.abspath(os.path.join(HERE, '..', '..', '.probe', '.lib', 'imageio_ffmpeg',
                                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2'))
LOGO = os.path.join(HERE, 'assets', 'gen', 'logo_b_0.jpg')
OUTDIR = os.path.join(HERE, '.tmp_intro_k2b')
OUT = os.path.join(HERE, 'out', 'intro_k2b_draft.mp4')
GEN = os.path.join(HERE, 'assets', 'gen')
REVIEW = os.path.join(HERE, 'assets', 'review')

RIB_TEXT = 'ЛМД · Ц. 67 КОП.'   # выбран заказчиком 2026-10-11; ЛМД = монетный двор (игра: «Лунный»)

W, H, FPS, DUR = 1920, 1080, 25, 7.4
NF = int(FPS * DUR)
GOLD_D = (150, 116, 52)
GOLD = (214, 176, 96)
GOLD_L = (246, 226, 164)
METAL_EDGE = (232, 206, 150)
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'


def pent(cx, cy, R, rot=-90):
    return [(cx + R * math.cos(math.radians(rot + k * 72)),
             cy + R * math.sin(math.radians(rot + k * 72))) for k in range(5)]


def ease(x):
    return x * x * (3 - 2 * x)


def eio(x):                       # ease-in-out cubic
    return 4 * x**3 if x < 0.5 else 1 - (-2 * x + 2)**3 / 2


def smoothstep(a, b, x):
    if b == a:
        return 0.0 if x < a else 1.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


class Znachek:
    """Пятиугольная призма: face (лого B), back (иллюминатор), боковая грань (ребро)."""

    def __init__(self, size=1200, rot=-90):
        self.size = size
        S = size
        cx = cy = S / 2
        self.cx, self.cy = cx, cy
        self.Rp = Rp = S * 0.49
        self.Rc = Rc = Rp * 0.68
        self.rot = rot

        # ---------- ЛИЦО ----------
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

        # ---------- ОБОРОТ (иллюминатор) ----------
        back = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(back)
        for r, col in [(Rp, GOLD_D), (Rp - 5, (176, 140, 66)), (Rp - 11, GOLD),
                       (Rp - 20, GOLD_L), (Rp - 30, GOLD), (Rp - 40, (196, 158, 82))]:
            d.polygon(pent(cx, cy, r, rot), fill=col)
        d.polygon(pent(cx, cy, Rp, rot), outline=(96, 72, 30, 255), width=3)
        d.ellipse([cx - Rc - 10, cy - Rc - 10, cx + Rc + 10, cy + Rc + 10], fill=(120, 92, 44, 255))
        d.ellipse([cx - Rc - 4, cy - Rc - 4, cx + Rc + 4, cy + Rc + 4], fill=(196, 158, 82, 255))
        glass = Image.new('RGBA', (int(Rc * 2), int(Rc * 2)), (8, 10, 22, 255))
        gd = ImageDraw.Draw(glass)
        rng = np.random.default_rng(11)
        for _ in range(240):
            sx = rng.uniform(0, Rc * 2); sy = rng.uniform(0, Rc * 2)
            rr = rng.uniform(0.6, 2.1)
            gd.ellipse([sx - rr, sy - rr, sx + rr, sy + rr],
                       fill=(210, 216, 240, int(rng.uniform(90, 235))))
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

        # ---------- РЕБРО (торец призмы) ----------
        t = S * 0.045
        self.rib_w = t
        rib = Image.new('RGBA', (int(t), S), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rib)
        yy = np.linspace(0, 1, S)[:, None]
        prof = 0.5 + 0.5 * np.sin(np.pi * yy)          # блик по длине ребра
        col = np.array(METAL_EDGE, float)[None, :]
        dark = np.array((120, 90, 40), float)[None, :]
        arr = dark + (col - dark) * prof
        arr = np.tile(arr[:, None, :], (1, int(t), 1)).astype(np.uint8)
        rib = Image.fromarray(arr, 'RGB').convert('RGBA')
        # кромки ребра (тёмные линии сверху/снизу)
        rd = ImageDraw.Draw(rib)
        rd.line([(0, 0), (t, 0)], fill=(96, 72, 30, 255), width=2)
        rd.line([(0, S - 1), (t, S - 1)], fill=(96, 72, 30, 255), width=2)
        self.rib = rib
        self.rib_text = RIB_TEXT

    def render_face(self, which, scale, persp_x):
        src = self.face if which == 'front' else self.back
        side = max(2, int(self.size * scale))
        im = src.resize((side, side), Image.LANCZOS)
        sx = max(0.02, abs(persp_x))
        im = im.resize((max(2, int(side * sx)), side), Image.LANCZOS)
        return im

    def rib_strip(self, h, persp_x):
        """Вертикальная полоса-ребро высотой h в перспективе (ширина = sin флипа)."""
        t = px = self.rib_w
        if persp_x < 0:                                # к обороте подписи не видно
            return None, 0
        wpx = max(1, int(t))
        edge = self.rib.resize((wpx, h), Image.LANCZOS)
        return edge, wpx


ZN = Znachek()
ZN.face.save(os.path.join(GEN, 'znachek_k1.png'))
ZN.back.save(os.path.join(GEN, 'znachek_k2_back.png'))
print('значки сохранены')


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
STARS = [(int(rng.integers(0, W)), int(rng.integers(0, H)), rng.uniform(0.6, 2.0), rng.uniform(0, 1))
         for _ in range(180)]


def draw_rib_engraving(canvas, cx, cy, avail_h, cap_h):
    """Выштамповать надпись на ребре: буквы вертикально (читаются снизу вверх).
    avail_h — доступная длина по ребру (высота значка*0.86); cap_h — высота строки."""
    probe = ImageFont.truetype(LATO_B, 100)
    unit = ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(ZN.rib_text, font=probe)
    f_sz = max(9, int(100 * (avail_h / unit)))
    f = ImageFont.truetype(LATO_B, f_sz)
    tw = ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(ZN.rib_text, font=f)
    cap = max(cap_h, f_sz + 6)
    txt = Image.new('RGBA', (int(tw) + 6, cap), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    ox = (cap - f_sz) // 2
    td.text((3 + 1, ox + 2), ZN.rib_text, font=f, fill=(232, 216, 176, 150))   # блик кромки
    td.text((3, ox), ZN.rib_text, font=f, fill=(112, 84, 38, 210))             # гравировка (мягкая, пасхалка)
    txt = txt.rotate(90, expand=True)
    canvas.alpha_composite(txt, (int(cx - txt.width / 2), int(cy - txt.height / 2)))


def paste_glow(bg, zn, cx_img, cy_img, glow):
    if glow > 0.03:
        big2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        big2.paste(zn, (cx_img, cy_img), zn)
        g = big2.filter(ImageFilter.GaussianBlur(26))
        ga = np.array(g).astype(np.float32)
        ga[:, :, :3] = np.clip(ga[:, :, :3] * 1.35 + np.array([255, 205, 120]), 0, 255)
        ga[:, :, 3] *= min(1.0, glow)
        bg = Image.alpha_composite(bg, Image.fromarray(ga.astype(np.uint8), 'RGBA'))
    return bg


def render(f):
    t = f / FPS
    bg = BG.copy()
    bd = ImageDraw.Draw(bg)
    tw = smoothstep(0.0, 1.6, t)
    for (sx, sy, sr, ph) in STARS:
        al = int(95 * tw * (0.5 + 0.5 * math.sin(t * 2.4 + ph * 6.28)))
        bd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(215, 220, 240, max(0, al)))
    bg = bg.convert('RGBA')

    # ============ ФАЗА 1: замах → флип → ПАУЗА НА РЕБРЕ → докрут (0 .. 3.9) ============
    if t < 4.15:
        if t < 0.9:                                   # замах: отход назад + лёгкий наклон
            p = ease(t / 0.9)
            sc = 0.94 + 0.05 * p
            theta = -0.16 * p                          # чуть «открываем» ребро заранее
        elif t < 1.9:                                 # быстрый флип до ребра (θ: -0.16 → π/2)
            p = eio((t - 0.9) / 1.0)
            theta = -0.16 + (math.pi / 2 + 0.16) * p
            sc = 0.99 + 0.03 * p
        elif t < 2.75:                                # ПАУЗА НА РЕБРЕ + умеренный наезд
            p = (t - 1.9) / 0.85
            theta = math.pi / 2 - 0.055 + 0.018 * math.sin(p * math.pi)  # держимся ПЕРЕД ребром
            sc = 1.02 + 0.66 * ease(p)                  # наезд: ребро видно крупно, знак в кадре
        elif t < 4.15:                                # отъезд назад и докрут до оборота
            p = eio((t - 2.75) / 1.40)
            theta = math.pi / 2 + (math.pi / 2) * p
            sc = 1.68 - 0.61 * ease(p)
        else:
            theta = math.pi; sc = 1.07

        persp = math.cos(theta)                        # +1 лицо ... 0 ребро ... -1 оборот
        edge_face = abs(math.sin(theta))               # 1 = смотрим точно в ребро
        glow = 0.18 + 0.55 * edge_face                 # вспышка металла на ребре

        zn = ZN.render_face('front' if persp >= 0 else 'back', sc * 0.62, persp)
        z = np.array(zn).astype(np.float32)
        a = z[:, :, 3:4] / 255.0
        z[:, :, :3] = np.clip(z[:, :, :3] + glow * 70 * a, 0, 255)
        zn = Image.fromarray(np.clip(z, 0, 255).astype(np.uint8), 'RGBA')
        cxi = int(W / 2 - zn.width / 2)
        cyi = int(H / 2 - zn.height / 2)
        bg = paste_glow(bg, zn, cxi, cyi, glow)

        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        layer.paste(zn, (cxi, cyi), zn)
        # РЕБРО-ПРИЗМА поверх (видно, когда значок почти на торце и лицо ещё спереди)
        if edge_face > 0.06 and persp > -0.02:
            # толщина ребра растёт с масштабом (в наезде — крупно) + преувеличена для читаемости
            wpx = max(2, int(zn.height * 0.14 * edge_face))
            strip = ZN.rib.resize((wpx, zn.height), Image.LANCZOS)
            sx = int(W / 2 + math.copysign(zn.width / 2, math.cos(theta) if abs(persp) > 1e-3 else 1))
            layer.alpha_composite(strip, (sx - wpx // 2, cyi))
            # гравировка читается в паузе у ребра (1.9–3.15 c)
            eng = smoothstep(1.95, 2.15, t) * (1 - smoothstep(2.70, 3.00, t))
            if eng > 0.05 and edge_face > 0.72:
                draw_rib_engraving(layer, sx, H / 2, zn.height * 0.80, wpx)
        bg = Image.alpha_composite(bg, layer)

    # ============ ФАЗА 2: зум внутрь иллюминатора (3.9 .. 5.7) ============
    if t >= 3.9:
        q = smoothstep(3.9, 5.7, t)
        st = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        for (sx, sy, sr, ph) in STARS:
            dx = (sx - W / 2); dy = (sy - H / 2)
            grow = 1.0 + q * 2.8
            x = W / 2 + dx * grow; y = H / 2 + dy * grow
            if not (0 <= x < W and 0 <= y < H):
                continue
            rr = sr * (1 + q * 2.2)
            al = int(200 * min(1.0, q * 1.6))
            sd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(220, 226, 245, al))
        st = st.filter(ImageFilter.GaussianBlur(1))
        bg = Image.alpha_composite(bg, st)
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
        na = smoothstep(4.2, 5.0, t)
        ma = np.array(mars).astype(np.float32)
        ma[:, :, 3] *= na
        bg = Image.alpha_composite(bg, Image.fromarray(np.clip(ma, 0, 255).astype(np.uint8), 'RGBA'))
        if t < 4.9:
            ra = 1 - smoothstep(4.1, 4.9, t)
            rim = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            rdw = ImageDraw.Draw(rim)
            rr = ZN.Rc * 0.62 * (1 + q * 3.4)
            rdw.ellipse([W / 2 - rr, H / 2 - rr, W / 2 + rr, H / 2 + rr],
                        outline=(214, 176, 96, int(220 * ra)), width=max(2, int(10 * ra)))
            bg = Image.alpha_composite(bg, rim)

    # ---- титул ----
    if t > 5.45:
        ta = smoothstep(5.5, 6.3, t)
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


if '--sheet' in sys.argv:
    T = [0.5, 1.4, 1.95, 2.25, 2.55, 2.95, 3.5, 6.6]
    sheet = Image.new('RGB', (4 * 480 + 20 * 5, 2 * 270 + 20 * 3), (16, 16, 20))
    for i, tt in enumerate(T):
        src = render(int(tt * FPS)).resize((480, 270), Image.LANCZOS)
        x = 20 + (i % 4) * (480 + 20); y = 20 + (i // 4) * (270 + 20)
        sheet.paste(src, (x, y))
        ImageDraw.Draw(sheet).text((x + 8, y + 6), '%.2f c' % tt,
                                   font=ImageFont.truetype(LATO, 22), fill=(255, 220, 120))
    sheet.save(os.path.join(REVIEW, 'review_36_intro_k2b.png'))
    print('лист:', os.path.relpath(os.path.join(REVIEW, 'review_36_intro_k2b.png'), HERE), sheet.size)
    sys.exit(0)

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
