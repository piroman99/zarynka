import urllib.request, urllib.parse, json, os, sys

PUB = "https://disk.yandex.ru/d/0oYY_-lGvJegj"
API = "https://cloud-api.yandex.net/v1/disk/public/resources"

def meta(path):
    q = urllib.parse.urlencode({"public_key": PUB, "path": path})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))

WANT = [
    "/game/script.rpy",
    "/game/options.rpy",
    "/game/screens.rpy",
    "/game/script_version.txt",
    "/game/fonts/burlak.ttf",
    "/game/images/sprites/za smile.png",
    "/game/images/Full/lobby.jpg",
    "/game/images/Full/za smile.jpg",
    "/game/images/bg/lobby.jpg",
    "/game/images/bg/4_/1st.jpg",
    "/game/images/gui/menu/igr.jpg",
    "/game/images/gui/menu/menu_ground.jpg",
    "/game/images/gui/menu/menu_hover.jpg",
    "/game/images/gui/menu/pref.jpg",
    "/game/images/gui/menu/zag.jpg",
    "/game/images/gui/yes_no/ground.jpg",
    "/game/images/gui/yes_no/hover.jpg",
    "/game/images/icons/icon.png",
    "/game/images/icons/icon_large.png",
    "/game/images/dissolves/lines.png",
    "/traceback.txt",
    "/errors.txt",
    "/МАСТХЕВ.txt",
]

os.makedirs("assets/orig", exist_ok=True)
ok = 0
for p in WANT:
    try:
        m = meta(p)
        url = m.get("file")
        if not url:
            print("SKIP (no file url)", p); continue
        dst = os.path.join("assets/orig", os.path.basename(p))
        if os.path.exists(dst) and os.path.getsize(dst) == m.get("size", -1):
            print("have ", dst); ok += 1; continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
        with open(dst, "wb") as f:
            f.write(data)
        print(f"ok    {dst}  ({len(data)} b)")
        ok += 1
    except Exception as e:
        print("ERR   ", p, type(e).__name__, e)
print(f"\ndownloaded {ok}/{len(WANT)}")
