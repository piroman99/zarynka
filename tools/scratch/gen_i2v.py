# -*- coding: utf-8 -*-
"""Оживление ключевых кадров AVM: image-to-video через hailuo-2-3 (6с, 768p, ~18.86 ₽).
Кадр заливаем в POST /v1/files (purpose=vision) -> file-pv id -> image_file_id.
Пишет mp4 в assets/gen/vid/. Цена под потолком max_price_rub=25.
"""
import os, json, uuid, urllib.request, urllib.error, time
import gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
OUT = os.path.join(HERE, "assets", "gen", "vid")
os.makedirs(OUT, exist_ok=True)

def upload(path, purpose="vision"):
    boundary = "----pv" + uuid.uuid4().hex
    data = open(path, "rb").read()
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="purpose"\r\n\r\n{purpose}\r\n'.encode()
    body += f"--{boundary}\r\n".encode()
    body += (f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\n'
             .encode())
    body += b"Content-Type: image/jpeg\r\n\r\n" + data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(pv.BASE + "/v1/files", data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                                          "Authorization": "Bearer " + pv._read_key(),
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["id"]

MOVE = ("Плавное киношное движение: медленный дрейф камеры вбок и лёгкий параллакс, "
        "спокойное естественное оживление кадра. НЕ менять композицию и объекты, не добавлять "
        "людей и текст, без резких движений и деформаций.")

JOBS = [
    ("ship",     "assets/gen/ok_space_ship_0.jpg",    MOVE),
    ("station",  "assets/gen/ok_space_station_0.jpg", MOVE),
    ("kate_suit","assets/gen/ok_kate_suit_0.jpg",
     "Плавное оживление: лёгкое дыхание и поворот головы, мягкий блик на шлеме, медленный "
     "дрейф камеры. Сохранить лицо, причёску и скафандр точно как на кадре, без искажений и "
     "без добавления текста."),
]

results = {}
for name, rel, prompt in JOBS:
    src = os.path.join(HERE, rel)
    print(f"\n=== {name} ===", flush=True)
    try:
        fid = upload(src)
        print(f"  file_id={fid}", flush=True)
        opts = {"duration": "6", "resolution": "768p", "image_file_id": fid}
        q = pv.price("hailuo-2-3", prompt, opts)
        print(f"  quote {q.get('priceRub')} ₽", flush=True)
        files, st = pv.generate_to_files("hailuo-2-3", prompt, opts,
                                         outdir="assets/gen/vid", name=f"i2v_{name}",
                                         max_price_rub=25)
        print(f"  [OK] {st.get('priceRub')} ₽ -> {[os.path.relpath(f, HERE) for f in files]}", flush=True)
        results[name] = files[0]
    except Exception as e:
        print(f"  [FAIL] {str(e)[:300]}", flush=True)

print("\nDONE", json.dumps({k: os.path.relpath(v, HERE) for k, v in results.items()}, ensure_ascii=False))
