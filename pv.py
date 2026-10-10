# -*- coding: utf-8 -*-
"""Минимальный клиент PlusVibe API для генерации изображений/видео/озвучки.

Ключ берётся по приоритету:
  1) env PLUSVIBE_API_KEY
  2) файл .pv_key            (одна строка: sk-pv-...)
  3) файл .api_keys.json     ({"plusvibe": "sk-pv-..."} или {"plusvibe": {"key": "..."}})

Из-за allowlist песочницы нужен доступ к хосту plusvibeapi.ru (проверено: открыт).
Результаты отдаются на том же хосте (/api/media/file/...?sig=...) — тоже достижимы.

Только стандартная библиотека + requests не нужен: используем urllib, чтобы не плодить зависимости.
"""
import os, json, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://plusvibeapi.ru"


def _read_key():
    k = os.environ.get("PLUSVIBE_API_KEY")
    if k:
        return k.strip()
    for name in (".pv_key", ".api_keys.json"):
        p = os.path.join(HERE, name)
        if os.path.exists(p):
            txt = open(p, encoding="utf-8").read().strip()
            if name.endswith(".json"):
                try:
                    d = json.loads(txt)
                    v = d.get("plusvibe") or d.get("PLUSVIBE_API_KEY") or d.get("key")
                    if isinstance(v, dict):
                        v = v.get("key")
                    if v:
                        return str(v).strip()
                except Exception:
                    pass
            elif txt:
                return txt
    raise RuntimeError("PlusVibe: не найден ключ. Положите его в .pv_key (sk-pv-...) "
                       "или .api_keys.json {\"plusvibe\":\"sk-pv-...\"}.")


def _req(method, path, body=None, extra_headers=None, timeout=90, auth=True):
    url = path if path.startswith("http") else BASE + path
    data = None
    headers = {"Accept": "application/json", "User-Agent": "nanobot-zaryanka/1.0"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if auth:
        headers["Authorization"] = "Bearer " + _read_key()
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            cost = r.headers.get("x-pv-cost-rub")
            return json.loads(raw) if raw else {}, cost
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"PlusVibe HTTP {e.code} {method} {path}: {raw[:400]}") from None


# ------------------------------------------------------------------ basics
def balance():
    d, _ = _req("GET", "/v1/balance")
    return d


def models(kind=None):
    path = "/v1/models?all=true" + (f"&type={kind}" if kind else "")
    d, _ = _req("GET", path)
    return d


def capabilities(model):
    d, _ = _req("GET", f"/api/model-capabilities/{model}", auth=False)
    return d


def price(model, prompt, opts=None):
    body = {"model": model, "prompt": prompt, "opts": opts or {}}
    d, cost = _req("POST", "/api/media/price", body)
    return d


# ---------------------------------------------------------------- generation
def generate(model, prompt, opts=None, *, strict=False, max_price_rub=None,
             idempotency=None, webhook_url=None):
    body = {"model": model, "prompt": prompt, "opts": opts or {}}
    if strict:
        body["strict"] = True
    if max_price_rub is not None:
        body["max_price_rub"] = max_price_rub
    if webhook_url:
        body["webhook_url"] = webhook_url
    extra = {"Idempotency-Key": idempotency} if idempotency else None
    d, cost = _req("POST", "/api/media/generate", body, extra)
    return d, cost  # d = {"ok":true,"jobId":...,"status":"processing"}


def job(job_id):
    d, _ = _req("GET", f"/api/media/jobs/{job_id}")
    return d


def wait(job_id, *, timeout=1800, poll0=3, poll_max=30, on_tick=None):
    t0 = time.time()
    delay = poll0
    while True:
        st = job(job_id)
        s = st.get("status")
        if on_tick:
            on_tick(s, st)
        if s in ("success", "fail"):
            return st
        if time.time() - t0 > timeout:
            raise TimeoutError(f"PlusVibe job {job_id} не завершился за {timeout}s (status={s})")
        time.sleep(delay)
        delay = min(poll_max, delay * 1.6)


def _sniff_ext(head):
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if head[:2] == b"\xff\xd8":
        return ".jpg"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return ".wav"
    if head[4:8] == b"ftyp":
        return ".mp4"
    if head[:3] == b"ID3" or head[:2] == b"\xff\xfb":
        return ".mp3"
    if head[:4] == b"OggS":
        return ".ogg"
    return ".bin"


def download(url, dest, timeout=300):
    """Скачивает результат и выставляет правильное расширение по магии файла."""
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "nanobot-zaryanka/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    base, ext = os.path.splitext(dest)
    if ext in ("", ".bin"):
        dest = base + _sniff_ext(data[:16])
    with open(dest, "wb") as f:
        f.write(data)
    return dest


def generate_to_files(model, prompt, opts=None, outdir="assets/gen", name="gen", **kw):
    d, cost = generate(model, prompt, opts, **kw)
    if not d.get("ok"):
        raise RuntimeError(f"generate не принят: {d}")
    jid = d["jobId"]
    print(f"[pv] job={jid} model={model} cost_header={cost}")
    st = wait(jid, on_tick=lambda s, _: print(f"[pv]   {s}"))
    if st.get("status") != "success":
        raise RuntimeError(f"job fail: {st.get('failMsg')} {st.get('errorCode')}")
    urls = st.get("resultUrls") or []
    files = []
    for i, u in enumerate(urls):
        ext = os.path.splitext(u.split("?")[0])[1] or ".bin"
        files.append(download(u, os.path.join(HERE, outdir, f"{name}_{i}{ext}")))
    print(f"[pv] ok: {len(files)} файл(ов), priceRub={st.get('priceRub')}")
    return files, st


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "balance":
        print(json.dumps(balance(), ensure_ascii=False, indent=2))
