# -*- coding: utf-8 -*-
"""Эмпирика: какие crop-параметры ВК принимает и что реально сохраняет.
Маркерная картинка: рамка magenta по периметру + цветные углы + сетка 10x6 + центр.
Использование: python3 _vk_cover_test.py [cw ch cx cy]
"""
import os, sys, json, base64, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vk
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VK = os.path.join(HERE, "assets", "vk")


def marker(path, W=1920, H=768):
    im = Image.new("RGB", (W, H), (30, 30, 30))
    d = ImageDraw.Draw(im)
    n = 10
    for i in range(n):
        x0 = i * W // n
        x1 = (i + 1) * W // n
        shade = 40 + int(200 * i / (n - 1))
        d.rectangle((x0, 0, x1, H), fill=(shade, shade, 60))
        d.text((x0 + 8, 12), str(i + 1), fill=(255, 255, 0))
        d.line((x0, 0, x0, H), fill=(255, 255, 255), width=2)
    for j in range(6):
        y = j * H // 6
        d.line((0, y, W, y), fill=(0, 200, 255), width=2)
        d.text((W - 40, y + 6), chr(65 + j), fill=(0, 255, 100))
    # углы
    S = 90
    for (bx, by, col, lab) in [(0, 0, (255, 0, 0), "TL"), (W - S, 0, (0, 255, 0), "TR"),
                               (0, H - S, (0, 0, 255), "BL"), (W - S, H - S, (255, 255, 0), "BR")]:
        d.rectangle((bx, by, bx + S, by + S), fill=col)
        d.text((bx + 30, by + 36), lab, fill=(0, 0, 0))
    d.rectangle((W // 2 - 40, H // 2 - 40, W // 2 + 40, H // 2 + 40), outline=(255, 0, 255), width=6)
    d.text((W // 2 - 34, H // 2 - 12), "MID", fill=(255, 0, 255))
    im.save(path, quality=95)
    return path


def read_cover(out_path):
    g = vk.call("groups.getById", group_id=vk.whoami()["id"], fields="cover")
    if isinstance(g, dict):
        g = g.get("groups", [g])[0]
    cov = g.get("cover", {})
    print("cover.enabled:", cov.get("enabled"))
    imgs = cov.get("images", [])
    print("cover.images:", [(i.get("width"), i.get("height")) for i in imgs])
    if not imgs:
        return None
    big = max(imgs, key=lambda i: i.get("width", 0) * i.get("height", 0))
    urllib.request.urlretrieve(big["url"], out_path)
    print("saved cover ->", out_path, big.get("width"), "x", big.get("height"))
    return out_path


def main():
    cw, ch = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1590, 400)
    cx, cy = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 0)
    src = sys.argv[5] if len(sys.argv) > 5 else marker(os.path.join(VK, "_diag_marker.png"))
    print("marker:", src)
    gid = vk.whoami()["id"]
    res = None
    for attempt in range(1, 7):
        up = vk.call("photos.getOwnerCoverPhotoUploadServer", group_id=gid,
                     crop_x=cx, crop_y=cy, crop_x2=cw, crop_y2=ch)["upload_url"]
        res = vk.upload(up, "photo", src)
        info = json.loads(base64.b64decode(res["photo"] + "=" * (-len(res["photo"]) % 4)).decode("utf-8", "replace"))
        print(f"try {attempt}: host={up.split('/')[2]} photo_info={info}")
        if not info.get("error"):
            break
    else:
        print("все попытки дали ошибку хранилища ВК")
        return
    sv = vk.call("photos.saveOwnerCoverPhoto", hash=res["hash"], photo=res["photo"])
    print("save ok:", json.dumps(sv, ensure_ascii=False)[:300])
    print("save ok:", json.dumps(sv, ensure_ascii=False)[:400])
    read_cover(os.path.join(VK, "_diag_out.png"))


if __name__ == "__main__":
    main()
