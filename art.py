"""Procedural painterly backgrounds & UI cards for the «Зарянка» VN prototype.

Everything here is placeholder art drawn with PIL/numpy so the pipeline is fully
playable *before* real sketches are dropped in. Swap = replace bg_*.png files.
"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

FONT_CANDIDATES_SERIF = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]
FONT_CANDIDATES_SANS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------- primitives
def vgrad(top, bottom, h=H, w=W):
    t = np.array(top, dtype=np.float32)
    b = np.array(bottom, dtype=np.float32)
    ramp = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    arr = (t[None, None, :] * (1 - ramp) + b[None, None, :] * ramp)
    arr = np.repeat(arr, w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def radial(img, cx, cy, r, color, strength=1.0, aspect=1.0):
    arr = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (xx - cx) / (r * aspect)
    dy = (yy - cy) / r
    d = np.sqrt(dx * dx + dy * dy)
    glow = np.clip(1.0 - d, 0.0, 1.0) ** 2
    glow *= strength
    col = np.array(color, dtype=np.float32)
    out = arr + glow[:, :, None] * col[None, None, :]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def stars(img, n, seed=1, ymax=H, bright=255, size=1):
    rnd = random.Random(seed)
    dr = ImageDraw.Draw(img)
    for _ in range(n):
        x = rnd.randint(0, W - 1)
        y = rnd.randint(0, ymax - 1)
        a = rnd.randint(60, bright)
        s = size if rnd.random() > 0.9 else max(1, size - 1)
        dr.ellipse([x, y, x + s, y + s], fill=(a, a, min(255, a + 20)))
    return img


def hills(draw, pts, color):
    draw.polygon(pts, fill=color)


def bench(draw, x, y, s=1.0, color=(40, 34, 30)):
    x2 = x + 150 * s
    y2 = y + 46 * s
    # seat
    draw.rectangle([x, y, x2, y + 10 * s], fill=color)
    # backrest
    draw.rectangle([x, y - 34 * s, x2, y - 26 * s], fill=color)
    for bx in (x + 6 * s, x + 70 * s, x + 132 * s):
        draw.rectangle([bx, y - 34 * s, bx + 7 * s, y + 10 * s], fill=color)
    # legs
    for lx in (x + 6 * s, x + 138 * s):
        draw.rectangle([lx, y + 10 * s, lx + 8 * s, y + 46 * s], fill=color)


def vignette(img, power=0.55):
    arr = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H / 2
    d = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    m = np.clip(1.0 - power * np.clip(d - 0.35, 0, None) ** 1.6, 0, 1)
    out = arr * m[:, :, None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def grain(img, amount=6, seed=3):
    rnd = np.random.default_rng(seed)
    arr = np.asarray(img).astype(np.float32)
    n = rnd.normal(0, amount, arr.shape[:2])[:, :, None]
    return Image.fromarray(np.clip(arr + n, 0, 255).astype(np.uint8), "RGB")


def spruce(draw, x, base, h, w, color):
    """fir tree silhouette"""
    tiers = 5
    for i in range(tiers):
        t = i / tiers
        ty = base - h * (1 - t)
        tw = w * (0.35 + 0.65 * t)
        draw.polygon([(x - tw / 2, ty), (x + tw / 2, ty), (x, ty - h / tiers * 1.35)], fill=color)
    draw.rectangle([x - w * 0.03, base - 4, x + w * 0.03, base + 10], fill=color)


# ---------------------------------------------------------------- backgrounds
def bg_space():
    img = vgrad((6, 10, 28), (2, 4, 12))
    img = stars(img, 260, seed=11)
    img = radial(img, 980, 500, 260, (150, 60, 40), 0.55)   # Mars glow
    img = radial(img, 200, 210, 300, (60, 120, 190), 0.5)   # Earth glow
    dr = ImageDraw.Draw(img, "RGBA")
    # Earth limb (lower-left)
    dr.ellipse([-260, 470, 380, 1110], fill=(28, 78, 150, 255))
    dr.ellipse([-260, 470, 380, 1110], outline=(120, 190, 255, 90), width=3)
    dr.arc([-260, 470, 380, 1110], 210, 330, fill=(180, 230, 255, 120), width=4)
    # Mars (upper-right), small
    dr.ellipse([940, 210, 1052, 322], fill=(190, 96, 64, 255))
    dr.ellipse([964, 240, 1010, 274], fill=(160, 74, 50, 255))
    # distant ship glint
    dr.line([1078, 400, 1120, 392], fill=(200, 220, 255, 180), width=2)
    return vignette(grain(img), 0.5)


def bg_star_city():
    """Звёздный городок, весна, административное здание"""
    img = vgrad((150, 195, 230), (208, 222, 226))
    img = radial(img, 980, 120, 320, (90, 70, 30), 0.35)   # sun haze
    dr = ImageDraw.Draw(img, "RGBA")
    # building
    dr.rectangle([150, 250, 1130, 620], fill=(196, 200, 205))
    dr.rectangle([150, 250, 1130, 275], fill=(150, 120, 96))
    for cx in range(200, 1100, 130):
        dr.rectangle([cx, 310, cx + 80, 440], fill=(120, 150, 175, 230))
        dr.rectangle([cx, 480, cx + 80, 600], fill=(120, 150, 175, 220))
    dr.rectangle([595, 300, 705, 620], fill=(80, 70, 64))   # entrance
    dr.rectangle([610, 430, 690, 620], fill=(120, 150, 175, 235))
    # ground
    dr.rectangle([0, 620, W, H], fill=(120, 126, 116))
    dr.rectangle([0, 618, W, 626], fill=(90, 96, 88))
    return vignette(grain(img), 0.45)


def bg_office():
    img = vgrad((52, 58, 72), (36, 40, 52))
    dr = ImageDraw.Draw(img, "RGBA")
    # big window right: bright daylight
    dr.rectangle([760, 90, 1180, 470], fill=(196, 214, 232))
    dr.rectangle([760, 90, 1180, 470], outline=(60, 60, 66), width=10)
    dr.line([970, 90, 970, 470], fill=(60, 60, 66), width=8)
    dr.line([760, 280, 1180, 280], fill=(60, 60, 66), width=8)
    # desk
    dr.polygon([(80, 560), (760, 520), (860, 600), (40, 640)], fill=(84, 60, 42))
    dr.rectangle([0, 600, W, H], fill=(46, 44, 48))
    # folder / papers
    dr.polygon([(330, 520), (560, 500), (585, 545), (350, 566)], fill=(232, 226, 210))
    dr.polygon([(300, 540), (470, 526), (490, 560), (318, 574)], fill=(214, 206, 190))
    return vignette(grain(img), 0.5)


def bg_alley():
    img = vgrad((168, 205, 232), (206, 220, 210))
    img = radial(img, 1180, 90, 300, (110, 90, 40), 0.4)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.rectangle([0, 600, W, H], fill=(140, 150, 130))     # ground
    # alley path
    dr.polygon([(470, 600), (810, 600), (1010, H), (270, H)], fill=(158, 152, 146))
    # spruces both sides
    for x in range(90, 470, 130):
        spruce(dr, x, 615, 250, 130, (34, 62, 46, 255))
    for x in range(830, 1220, 130):
        spruce(dr, x, 615, 250, 130, (34, 62, 46, 255))
    # wrought gate hint
    dr.arc([560, 300, 760, 560], 200, 340, fill=(70, 70, 74), width=5)
    bench(dr, 470, 590, 1.0, (60, 52, 46))
    return vignette(grain(img), 0.45)


def bg_pool():
    img = vgrad((30, 66, 96), (14, 36, 60))
    dr = ImageDraw.Draw(img, "RGBA")
    # water line
    dr.rectangle([0, 300, W, H], fill=(24, 78, 118, 255))
    for i in range(0, H, 26):
        dr.line([0, 300 + i, W, 300 + i], fill=(40, 110, 150, 40), width=2)
    # caustics
    img = radial(img, 640, 300, 520, (70, 150, 190), 0.35)
    # submerged station mockup
    dr.rectangle([430, 380, 810, 600], fill=(52, 66, 74, 210), outline=(120, 150, 160, 160), width=4)
    dr.rectangle([560, 300, 660, 380], fill=(48, 60, 70, 210), outline=(120, 150, 160, 150), width=3)
    dr.ellipse([600, 320, 620, 340], fill=(150, 200, 220, 180))
    # balcony rail top
    dr.rectangle([0, 60, W, 74], fill=(60, 62, 66))
    dr.rectangle([0, 74, 14, 300], fill=(60, 62, 66))
    return vignette(grain(img), 0.55)


def bg_yard_summer():
    img = vgrad((150, 192, 228), (232, 208, 162))
    img = radial(img, 300, 130, 380, (120, 90, 40), 0.45)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.rectangle([0, 590, W, H], fill=(150, 140, 108))
    dr.polygon([(0, 590), (W, 590), (W, 640), (0, 640)], fill=(122, 132, 96))  # grass strip
    # jasmine bushes
    for cx, r, c in [(180, 150, (74, 96, 60)), (330, 120, (86, 108, 66)), (1050, 160, (70, 92, 58))]:
        dr.ellipse([cx - r, 590 - r, cx + r, 590 + r // 2], fill=c + (255,))
    # tiny white blossoms
    rnd = random.Random(7)
    for _ in range(60):
        x = rnd.uniform(20, 380); y = rnd.uniform(470, 590)
        dr.ellipse([x, y, x + 5, y + 5], fill=(250, 248, 240, 220))
    bench(dr, 600, 580, 1.15, (58, 48, 42))
    return vignette(grain(img), 0.42)


def bg_winter_office():
    img = vgrad((40, 46, 60), (26, 30, 40))
    dr = ImageDraw.Draw(img, "RGBA")
    # window: snowy park
    dr.rectangle([720, 80, 1180, 460], fill=(210, 220, 234))
    dr.rectangle([720, 80, 1180, 460], outline=(52, 54, 60), width=10)
    dr.line([950, 80, 950, 460], fill=(52, 54, 60), width=8)
    for x in (800, 900, 1040, 1120):
        spruce(dr, x, 440, 150, 90, (150, 162, 178, 255))
    dr.rectangle([720, 430, 1180, 460], fill=(232, 238, 246))
    # long desk
    dr.polygon([(60, 560), (760, 520), (880, 600), (20, 650)], fill=(70, 50, 36))
    dr.rectangle([0, 600, W, H], fill=(38, 36, 42))
    dr.polygon([(300, 512), (520, 494), (545, 536), (320, 556)], fill=(226, 220, 206))
    return vignette(grain(img), 0.52)


def bg_dacha():
    img = vgrad((186, 214, 236), (242, 214, 158))
    img = radial(img, 980, 150, 420, (130, 100, 40), 0.5)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.rectangle([0, 560, W, H], fill=(120, 104, 74))
    dr.rectangle([0, 556, W, 566], fill=(96, 82, 58))
    # veranda beams
    dr.rectangle([0, 0, W, 60], fill=(96, 70, 46))
    for x in range(80, W, 210):
        dr.rectangle([x, 60, x + 24, 560], fill=(104, 78, 52))
    # railing
    dr.rectangle([0, 470, W, 486], fill=(120, 92, 62))
    for x in range(40, W, 90):
        dr.rectangle([x, 486, x + 14, 560], fill=(112, 86, 58))
    # distant meadow/trees
    dr.rectangle([0, 540, W, 560], fill=(120, 150, 96))
    # rocking chair + table hint
    dr.ellipse([820, 520, 1040, 600], fill=(74, 56, 40))
    dr.rectangle([660, 470, 800, 560], fill=(70, 54, 40))
    dr.ellipse([690, 452, 780, 496], fill=(228, 224, 214))
    return vignette(grain(img), 0.4)


def bg_luna():
    img = vgrad((2, 3, 8), (6, 8, 14))
    img = stars(img, 300, seed=21)
    dr = ImageDraw.Draw(img, "RGBA")
    # Earth in the sky
    dr.ellipse([210, 90, 330, 210], fill=(46, 108, 178, 255))
    dr.ellipse([236, 118, 268, 146], fill=(90, 150, 90, 255))
    dr.arc([210, 90, 330, 210], 200, 300, fill=(180, 220, 255, 150), width=3)
    # lunar surface
    dr.ellipse([-200, 560, 1480, 1200], fill=(150, 148, 146))
    for cx, cy, r in [(300, 640, 70), (700, 600, 40), (1000, 660, 90), (520, 700, 30)]:
        dr.ellipse([cx - r, cy - r, cx + r, cy + r * 0.5], fill=(120, 118, 116))
    # base dome + windows
    dr.ellipse([820, 470, 1080, 700], fill=(180, 182, 186), outline=(210, 214, 220), width=4)
    dr.ellipse([860, 520, 940, 600], fill=(120, 200, 230, 220))
    dr.ellipse([960, 520, 1040, 600], fill=(120, 200, 230, 220))
    # bench with flowers hint
    bench(dr, 360, 600, 1.0, (120, 118, 116))
    rnd = random.Random(9)
    for _ in range(40):
        x = rnd.uniform(300, 520); y = rnd.uniform(560, 640)
        dr.ellipse([x, y, x + 4, y + 6], fill=(240, 244, 248, 230))
    return vignette(grain(img), 0.5)


BG = {
    "space": bg_space,
    "city": bg_star_city,
    "office": bg_office,
    "alley": bg_alley,
    "pool": bg_pool,
    "yard": bg_yard_summer,
    "winter": bg_winter_office,
    "dacha": bg_dacha,
    "luna": bg_luna,
}


def render_backgrounds():
    os.makedirs(ASSETS, exist_ok=True)
    out = {}
    for key, fn in BG.items():
        p = os.path.join(ASSETS, f"bg_{key}.png")
        fn().save(p)
        out[key] = p
        print("bg", key, "->", p)
    return out


if __name__ == "__main__":
    render_backgrounds()
