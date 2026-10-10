# -*- coding: utf-8 -*-
"""Подписанные (presigned) ссылки на выложенные клипы + проверка доступности."""
import datetime as dt
import hashlib
import hmac
import importlib.util
import os
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
S3_PATH = os.path.abspath(os.path.join(HERE, "..", "..", "no62_audit", "android", "_s3.py"))
spec = importlib.util.spec_from_file_location("s3", S3_PATH)
s3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s3)

TTL = 604800
KEYS = ["zaryanka/clips/avm_v3_epic_9x16.mp4", "zaryanka/clips/avm_v3_epic.mp4"]


def presign(key, ttl=TTL):
    now = dt.datetime.now(dt.timezone.utc)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")
    scope = f"{datestamp}/{s3.REGION}/s3/aws4_request"
    path = "/" + s3.BUCKET + "/" + key
    q = {
        "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
        "X-Amz-Credential": f"{s3.AK}/{scope}",
        "X-Amz-Date": amzdate,
        "X-Amz-Expires": str(ttl),
        "X-Amz-SignedHeaders": "host",
    }
    cq = "&".join(f"{s3._enc(k, safe='')}={s3._enc(v, safe='')}" for k, v in sorted(q.items()))
    cr = "\n".join(["GET", path, cq, f"host:{s3.HOST}\n", "host", "UNSIGNED-PAYLOAD"])
    sts = "\n".join(["AWS4-HMAC-SHA256", amzdate, scope,
                     hashlib.sha256(cr.encode()).hexdigest()])
    sig = hmac.new(s3._signing_key(s3.SK, datestamp, s3.REGION, "s3"),
                   sts.encode(), hashlib.sha256).hexdigest()
    return f"{s3.SCHEME}://{s3.HOST}{path}?{cq}&X-Amz-Signature={sig}"


for k in KEYS:
    url = presign(k)
    try:
        req = urllib.request.Request(url, headers={"Range": "bytes=0-1023"})
        with urllib.request.urlopen(req, timeout=60) as r:
            chunk = r.read()
            print("OK", r.status, "sample", len(chunk), "B; total",
                  r.headers.get("Content-Range"), k)
    except Exception as e:
        print("ERR", repr(e)[:150], k)
    print(url)
    print()
