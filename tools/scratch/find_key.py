# -*- coding: utf-8 -*-
"""Поиск ключа PlusVibe / следов конфигурации. Только чтение."""
import os, re, glob, json

HOME = os.path.expanduser("~")
WS = "/home/ivan/.nanobot/workspace"

print("=== 1. ENV (маскирую значения) ===")
for k, v in sorted(os.environ.items()):
    if re.search(r"pv|vibe|plusvibe|api|key|token|secret|openai|anthropic|base_url|baseurl", k, re.I):
        sv = (v[:6] + "…" + str(len(v))) if v and len(v) > 8 else "(short)"
        print(f"  {k} = {sv}")

print("\n=== 2. ~/.nanobot/config.json ===")
cfg = os.path.join(HOME, ".nanobot", "config.json")
if os.path.exists(cfg):
    try:
        d = json.load(open(cfg, encoding="utf-8"))
        def walk(o, p=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, p + "." + k)
            elif isinstance(o, list):
                for i, v in enumerate(o[:5]):
                    walk(v, p + f"[{i}]")
            else:
                s = str(o)
                if re.search(r"sk-pv|plusvibe|apiKey|api_key|base_url|baseUrl|Bearer", p, re.I) or re.search(r"sk-|https?://", s):
                    if any(x in p.lower() for x in ("key", "url", "token", "provider", "model", "base")):
                        show = s if len(s) < 12 else s[:8] + "…(" + str(len(s)) + ")"
                        print(f"  {p} = {show}")
        walk(d)
        print("  [OK] config прочитан")
    except Exception as e:
        print("  ERR", type(e).__name__, e)
else:
    print("  нет файла", cfg)

print("\n=== 3. файлы с 'sk-pv-' или 'plusvibe' в workspace и ~/.nanobot ===")
roots = [WS, os.path.join(HOME, ".nanobot")]
pat = re.compile(rb"sk-pv-|plusvibe", re.I)
hits = 0
for r in roots:
    for dp, dn, fn in os.walk(r):
        if any(seg in dp for seg in (".git", "node_modules", ".tools", "__pycache__")):
            continue
        for f in fn:
            p = os.path.join(dp, f)
            try:
                if os.path.getsize(p) > 3_000_000:
                    continue
                with open(p, "rb") as fh:
                    b = fh.read()
                if pat.search(b):
                    print("  HIT:", p)
                    hits += 1
            except Exception:
                pass
print("  всего совпадений:", hits)

print("\n=== 4. .env-подобные файлы ===")
for r in roots:
    for name in (".env", "env", ".api_keys.json", ".pv_key"):
        for p in glob.glob(os.path.join(r, "**", name), recursive=True):
            print("  есть:", p)
