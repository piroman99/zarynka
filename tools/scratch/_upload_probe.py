# -*- coding: utf-8 -*-
"""Upload с purpose=vision -> file-pv id -> цена hailuo-2-3 i2v через image_file_id."""
import os, json, uuid, urllib.request, urllib.error, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
ship = os.path.join(HERE, "assets/gen/ok_space_ship_0.jpg")

def upload(path, purpose="vision"):
    boundary = "----pv" + uuid.uuid4().hex
    name = os.path.basename(path)
    data = open(path, "rb").read()
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="purpose"\r\n\r\n{purpose}\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'.encode()
    body += b"Content-Type: image/jpeg\r\n\r\n" + data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(pv.BASE + "/v1/files", data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                                          "Authorization": "Bearer " + pv._read_key(),
                                          "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]
    except Exception as e:
        return None, str(e)[:300]

st, res = upload(ship)
print("upload:", st, json.dumps(res, ensure_ascii=False)[:400] if isinstance(res, dict) else res)

fid = None
if isinstance(res, dict):
    fid = res.get("id") or (res.get("data") or {}).get("id")
print("file id:", fid)

if fid:
    for dur, res_ in (("6", "768p"), ("6", "1080p")):
        try:
            q = pv.price("hailuo-2-3", "лёгкий дрейф камеры", {"duration": dur, "resolution": res_,
                                                              "image_file_id": fid})
            print(f"hailuo-2-3 {dur}s {res_} via file_id -> {q.get('priceRub')} ₽")
        except Exception as e:
            msg = str(e); msg = msg.split('"message":"')[1].split('"')[0] if '"message":"' in msg else msg[:110]
            print(f"hailuo-2-3 {dur}s {res_} ERR {msg}")
