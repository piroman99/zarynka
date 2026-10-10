# -*- coding: utf-8 -*-
"""Читаем НАСТОЯЩИЙ конфиг nanobot по абсолютному пути + ищем ключ PlusVibe."""
import os, re, json, glob

CFG = "/home/ivan/.nanobot/config.json"
print("exists:", os.path.exists(CFG))
if os.path.exists(CFG):
    d = json.load(open(CFG, encoding="utf-8"))
    print("top-level keys:", list(d.keys()))
    raw = json.dumps(d, ensure_ascii=False)
    for kw in ["plusvibe", "sk-pv", "pv", "mcp", "media", "image"]:
        print(f"  содержит '{kw}':", bool(re.search(kw, raw, re.I)))
    # providers
    prov = d.get("providers", {})
    for name, val in (prov.items() if isinstance(prov, dict) else []):
        if isinstance(val, dict):
            k = val.get("apiKey") or val.get("api_key") or ""
            bu = val.get("baseUrl") or val.get("base_url") or ""
            print(f"  provider[{name}] base={bu!r} key={'есть('+str(len(k))+')' if k else 'нет'}")
    # mcpServers
    tools = d.get("tools", {})
    print("tools keys:", list(tools.keys()) if isinstance(tools, dict) else tools)
    if isinstance(tools, dict) and tools.get("mcpServers"):
        print("mcpServers:", list(tools["mcpServers"].keys()))

print("\n=== любые sk-pv в ~/.nanobot (кроме workspace) ===")
for p in glob.glob("/home/ivan/.nanobot/**/*", recursive=True):
    if os.path.isfile(p):
        try:
            if os.path.getsize(p) > 2_000_000:
                continue
            with open(p, "rb") as f:
                b = f.read()
            if b"sk-pv" in b:
                print("  HIT", p)
        except Exception:
            pass

print("\n=== .vps / .deploy ключи (не тот, но вдруг) ===")
for p in glob.glob("/home/ivan/.nanobot/workspace/**/.vps/**", recursive=True)[:10]:
    print("  ", p)
print("HOME env:", os.environ.get("HOME"))
