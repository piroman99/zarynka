# -*- coding: utf-8 -*-
"""Выложить видео «Зарянки» в S3 и получить скачиваемые ссылки.
Использует существующий SigV4-клиент no62_audit/android/_s3.py и тот же бакет/env.
  python3 vk_share.py            — выложить оба тизера (16:9 и 9:16) и напечатать ссылки
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
S3_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "no62_audit", "android", "_s3.py"))

spec = importlib.util.spec_from_file_location("s3", S3_PATH)
s3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s3)

TTL = 604800  # 7 дней (максимум для presigned URL)
JOBS = [
    ("out/avm_v3_epic_9x16.mp4", "zaryanka/clips/avm_v3_epic_9x16.mp4"),
    ("out/avm_v3_epic.mp4", "zaryanka/clips/avm_v3_epic.mp4"),
]

if __name__ == "__main__":
    for local, key in JOBS:
        lp = os.path.join(HERE, local)
        if not os.path.exists(lp):
            print("нет файла:", local); continue
        with open(lp, "rb") as f:
            data = f.read()
        code, _h, body = s3.request_h(
            "PUT", key, body=data,
            headers={"content-type": "video/mp4", "content-length": str(len(data))},
            timeout=600)
        print(f"PUT {key} -> HTTP {code} ({len(data)} B)")
        if code >= 300:
            print("  ", body[:300])
