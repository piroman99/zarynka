# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, json, os, time
from PIL import Image, ImageDraw, ImageFont

PUB = "https://disk.yandex.ru/d/0oYY_-lGvJegj"
API = "https://cloud-api.yandex.net/v1/disk/public/resources"

def meta(path):
    q = urllib.parse.urlencode({"public_key": PUB, "path": path})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def fetch(path, outname, tries=4):
    for t in range(tries):
        try:
            m = meta(path)
            url = m.get("file")
            if not url: return None
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
            if len(data) != m.get("size", len(data)):
                raise IOError("short read")
            dst = os.path.join("assets/orig", outname)
            open(dst, "wb").write(data)
            print("ok", dst, len(data)); return dst
        except Exception as e:
            print(f"try{t} err {path}: {type(e).__name__} {e}")
            time.sleep(3)
    return None

# 1) decode МАСТХЕВ
raw = open("assets/orig/МАСТХЕВ.txt", "rb").read()
for enc in ("cp1251", "koi8-r", "utf-8"):
    try:
        print(f"--- МАСТХЕВ ({enc}) ---")
        print(raw.decode(enc))
        break
    except Exception as e:
        print(enc, "fail", e)

# 2) re-download colliding / failed
fetch("/game/fonts/burlak.ttf", "burlak.ttf")
fetch("/game/images/bg/4_/1st.jpg", "bg_4_1st.jpg")
fetch("/game/images/Full/lobby.jpg", "full_lobby.jpg")
fetch("/game/images/gui/yes_no/ground.jpg", "yn_ground.jpg")
fetch("/game/images/gui/yes_no/hover.jpg", "yn_hover.jpg")

# 3) contact sheet of orig images
imgs = [f for f in os.listdir("assets/orig") if f.lower().endswith((".png", ".jpg"))]
imgs.sort()
cols, tw, th = 4, 300, 200
rows = (len(imgs) + cols - 1) // cols
sheet = Image.new("RGB", (tw * cols, (th + 20) * rows), (16, 16, 18))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
for i, n in enumerate(imgs):
    try:
        im = Image.open(os.path.join("assets/orig", n)).convert("RGB")
    except Exception:
        continue
    im.thumbnail((tw, th))
    x = (i % cols) * tw; y = (i // cols) * (th + 20)
    sheet.paste(im, (x + (tw - im.width) // 2, y + 20))
    d.text((x + 5, y + 3), n[:38], font=f, fill=(235, 235, 235))
sheet.save("assets/orig/_orig_contact.png")
print("sheet:", sheet.size, "imgs:", imgs)
