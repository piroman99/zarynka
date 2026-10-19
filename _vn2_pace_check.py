# -*- coding: utf-8 -*-
"""Замер темпа: интервал между страницами в авто-режиме при PACE=0.8 (по умолчанию) и 1.0.
Доказывает, что «на 20% быстрее» реально применилось в движке."""
import os, sys, time, statistics, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

POS = "window.__DBG ? window.__DBG.pos : -1"


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def measure(b, port, pace, n=8):
    url = "http://127.0.0.1:%d/vn2/index.html?auto=1&music=0&pace=%s" % (port, pace)
    b.navigate(url, wait=1.2)
    b.js("document.getElementById('start').click()")
    time.sleep(0.4)
    b.js("document.getElementById('vskip').click()")
    time.sleep(0.5)
    stamps, last = [], None
    t_end = time.time() + 90
    while time.time() < t_end and len(stamps) <= n:
        pos = b.js(POS)
        if pos is not None and pos != last:
            last = pos
            stamps.append(time.time())
        time.sleep(0.03)
    return [round((y - x) * 1000) for x, y in zip(stamps, stamps[1:])]


def main():
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    b = Browser(1280, 720)
    res = {}
    try:
        for pace in ("0.8", "1.0"):
            gaps = measure(b, port, pace)
            gaps = gaps[1:] if len(gaps) > 2 else gaps
            res[pace] = gaps
            med = statistics.median(gaps) if gaps else 0
            print("pace=%s: шагов %d, интервалы мс %s, медиана %s" % (pace, len(gaps), gaps, round(med)))
        if res.get("0.8") and res.get("1.0"):
            a, c = statistics.median(res["0.8"]), statistics.median(res["1.0"])
            print("\nотношение 0.8/1.0 = %.3f   (ожидание ~0.80)" % (a / c))
    finally:
        b.close()
        srv.shutdown()


main()
