# -*- coding: utf-8 -*-
"""1) Тест POST /v1/files (multipart) -> file-pv id. 2) Цены i2v на разных движках."""
import os, json, uuid, urllib.request, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
ship = os.path.join(HERE, "assets/gen/ok_space_ship_0.jpg")

# ---- 1. multipart upload
def upload(path):
    boundary = "----pv" + uuid.uuid4().hex
    name = os.path.basename(path)
    data = open(path, "rb").read()
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'.encode()
    body += b"Content-Type: image/jpeg\r\n\r\n" + data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(pv.BASE + "/v1/files", data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                                          "Authorization": "Bearer " + pv._read_key(),
                                          "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read().decode()[:600]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]
    except Exception as e:
        return None, str(e)[:300]

print("=== POST /v1/files ===")
print(upload(ship))

# ---- 2. цены i2v на разных движках
img = gen.b64(ship)
models = ["kling-v2-5-turbo", "kling-v3-turbo", "seedance-2-0-mini", "seedance-2.0",
          "wan-2-2", "wan-2-5", "pixverse-v6", "hailuo-2-3", "minimax-h3-turbo"]
print("\n=== i2v prices (image_url proxy, 5s) ===")
for m in models:
    try:
        c = pv.capabilities(m)
        op = c["operations"][0]
        props = op["requestJsonSchema"]["properties"].get("opts", {}).get("properties", {})
        keys = list(props.keys())
        q = pv.price(m, "лёгкое движение камеры", {"image_url": "https://example.com/a.jpg"})
        print(f"{m:22s} {q.get('priceRub')} ₽  opts={keys}")
    except Exception as e:
        msg = str(e)
        msg = msg.split('"message":"')[1].split('"')[0] if '"message":"' in msg else msg[:110]
        print(f"{m:22s} ERR {msg}")
