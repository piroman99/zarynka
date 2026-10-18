# -*- coding: utf-8 -*-
"""pv_check_models.py — быстрый чек-лист по чат-моделям PlusVibe.

Запуск:  python3 pv_check_models.py qwen3.8-omni-flash xiaomi/mimo-v2.5
Печатает по каждой модели: текст, stream, tools, stream+tools, картинка (https),
реакцию на max_tokens и длину reasoning. Стоит копейки (<0.1 ₽ на модель).
"""
import json, os, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

TOOLS = [{"type": "function", "function": {
    "name": "read_file", "description": "Read a file",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}},
                   "required": ["path"]}}}]
IMG = "https://raw.githubusercontent.com/piroman99/zarynka/rebuild/vn2/img/char/kate.png"


def plain(model, **extra):
    body = {"model": model, "messages": [{"role": "user", "content": "Ответь: ОК"}],
            "max_tokens": 20}
    body.update(extra)
    t0 = time.time()
    r, cost = pv._req("POST", "/v1/chat/completions", body, timeout=180)
    ch = (r.get("choices") or [{}])[0]
    msg = ch.get("message") or {}
    u = r.get("usage") or {}
    return (f"{time.time()-t0:.1f}s finish={ch.get('finish_reason')} "
            f"prompt={u.get('prompt_tokens')} comp={u.get('completion_tokens')} "
            f"reason={len(msg.get('reasoning_content') or '')} "
            f"tool_calls={bool(msg.get('tool_calls'))} "
            f"text={(msg.get('content') or '')[:40]!r} cost={cost}")


def stream(model, with_tools):
    body = {"model": model, "stream": True,
            "messages": [{"role": "user", "content": "Прочитай файл /etc/hostname"}]}
    if with_tools:
        body["tools"] = TOOLS
    req = urllib.request.Request(pv.BASE + "/v1/chat/completions",
                                data=json.dumps(body).encode(), method="POST",
                                headers={"Content-Type": "application/json",
                                         "Accept": "text/event-stream",
                                         "Authorization": "Bearer " + pv._read_key()})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            raw = r.read().decode("utf-8", "replace")
        return (f"{time.time()-t0:.1f}s chunks={raw.count('data:')} "
                f"tool_calls={'tool_calls' in raw} done={'[DONE]' in raw}")
    except Exception as e:
        return f"ERR {str(e)[:140]}"


def image(model):
    body = {"model": model, "max_tokens": 60, "reasoning_effort": "none",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": "Кто на картинке? Одно слово."},
                {"type": "image_url", "image_url": {"url": IMG}}]}]}
    try:
        r, cost = pv._req("POST", "/v1/chat/completions", body, timeout=180)
        txt = ((r.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        return f"OK {(txt[:60] or '').strip()!r} cost={cost}"
    except Exception as e:
        return f"ERR {str(e)[:140]}"


def main(models):
    for m in models:
        print("=" * 74)
        print(m)
        for label, fn in (
            ("текст", lambda: plain(m)),
            ("текст, reasoning_effort=none", lambda: plain(m, reasoning_effort="none")),
            ("stream", lambda: stream(m, False)),
            ("stream+tools", lambda: stream(m, True)),
            ("tools (no stream)", lambda: plain(m, tools=TOOLS)),
            ("картинка по https", lambda: image(m)),
            ("max_tokens=1", lambda: plain(m, max_tokens=1)),
        ):
            try:
                print(f"  {label:30s} {fn()}")
            except Exception as e:
                print(f"  {label:30s} ERR {str(e)[:150]}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["qwen3.8-omni-flash", "xiaomi/mimo-v2.5"])
