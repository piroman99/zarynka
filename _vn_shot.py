# -*- coding: utf-8 -*-
"""Снимает экраны VN-прототипа и проверяет PWA (manifest + service worker).
Запуск из корня workspace:  .venv/bin/python novella/zaryanka/_vn_shot.py
"""
import functools, http.server, os, socketserver, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(os.path.dirname(HERE))
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", os.path.join(WS, ".playwright-browsers"))

SHOTS = os.path.join(HERE, "_shots_vn")
os.makedirs(SHOTS, exist_ok=True)
PORT = 8791


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    httpd.allow_reuse_address = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main():
    from playwright.sync_api import sync_playwright

    httpd = serve()
    url = f"http://127.0.0.1:{PORT}/vn/index.html"
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--use-gl=swiftshader", "--no-sandbox", "--hide-scrollbars"])
        pg = br.new_page(viewport={"width": 1280, "height": 720})
        logs = []
        pg.on("console", lambda m: logs.append(m.text))
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(600)

        # PWA checks
        manifest = pg.get_attribute('link[rel="manifest"]', "href")
        sw = pg.evaluate("!!navigator.serviceWorker")
        reg = pg.evaluate("navigator.serviceWorker.getRegistrations().then(r=>r.length)")
        pg.wait_for_timeout(700)
        reg2 = pg.evaluate("navigator.serviceWorker.getRegistrations().then(r=>r.length)")
        print("manifest:", manifest, "| SW api:", sw, "| registrations:", reg, "->", reg2)

        pg.screenshot(path=os.path.join(SHOTS, "01_title.png"))

        def state():
            return pg.evaluate("({c:document.getElementById('chapter').textContent,"
                               "n:document.getElementById('name').textContent,"
                               "t:document.getElementById('text').textContent})")

        def advance():
            pg.click("#stage"); pg.wait_for_timeout(140)

        # Старт
        pg.click("#start"); pg.wait_for_timeout(500)

        # идём до сцены «Екатерина Ивановна» + реплика Сергея
        guard = 0
        while guard < 40:
            s = state()
            if s["c"] == "Екатерина Ивановна" and "Лихнецкий" in s["n"]:
                break
            advance(); guard += 1
        pg.wait_for_timeout(300)
        print("frame2:", state())
        pg.screenshot(path=os.path.join(SHOTS, "02_kate_dialog.png"))

        # до аллеи, до реплики поэта (Лёша)
        guard = 0
        while guard < 120:
            s = state()
            if s["c"] == "На аллее" and "Лёша" in s["n"]:
                break
            advance(); guard += 1
        pg.wait_for_timeout(300)
        print("frame3:", state())
        pg.screenshot(path=os.path.join(SHOTS, "03_alley.png"))

        # до финала эпизода
        guard = 0
        while guard < 160:
            if pg.evaluate("document.getElementById('end').classList.contains('show')"):
                break
            advance(); guard += 1
        pg.wait_for_timeout(600)
        ended = pg.evaluate("document.getElementById('end').classList.contains('show')")
        print("end screen shown:", ended)
        pg.screenshot(path=os.path.join(SHOTS, "04_end.png"))

        br.close()
    httpd.shutdown()
    print("shots ->", SHOTS)


if __name__ == "__main__":
    main()
