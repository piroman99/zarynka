# -*- coding: utf-8 -*-
"""Снимает экраны VN-прототипа, проверяет PWA, музыку и кинозал (AVM).
Запуск из корня workspace:  .venv/bin/python novella/zaryanka/_vn_shot.py
"""
import functools, http.server, os, socketserver, threading

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(os.path.dirname(HERE))
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", os.path.join(WS, ".playwright-browsers"))

SHOTS = os.path.join(HERE, "_shots_vn")
os.makedirs(SHOTS, exist_ok=True)
PORT = 8791


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)

    class Srv(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    httpd = Srv(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main():
    from playwright.sync_api import sync_playwright

    httpd = serve()
    url = f"http://127.0.0.1:{PORT}/vn/index.html"
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--use-gl=swiftshader", "--no-sandbox",
                                     "--hide-scrollbars", "--autoplay-policy=no-user-gesture-required"])
        pg = br.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(700)

        # PWA
        reg = pg.evaluate("navigator.serviceWorker.getRegistrations().then(r=>r.length)")
        print("PWA service worker registrations:", reg)

        pg.screenshot(path=os.path.join(SHOTS, "01_title.png"))

        def state():
            return pg.evaluate("({c:document.getElementById('chapter').textContent,"
                               "n:document.getElementById('name').textContent,"
                               "t:document.getElementById('text').textContent})")

        def advance():
            pg.click("#stage"); pg.wait_for_timeout(150)

        # --- кинозал: тизер с тайтла ---
        pg.click("#teaser"); pg.wait_for_timeout(1200)
        cin = pg.evaluate("({open:!document.getElementById('cinema').hidden,"
                          "paused:document.getElementById('avm').paused,"
                          "t:document.getElementById('avm').currentTime,"
                          "dur:document.getElementById('avm').duration})")
        print("cinema (тизер):", cin)
        pg.screenshot(path=os.path.join(SHOTS, "05_teaser.png"))
        pg.click("#skip"); pg.wait_for_timeout(600)

        # --- старт: музыка ---
        pg.click("#start"); pg.wait_for_timeout(1400)
        a = pg.evaluate("({paused:document.getElementById('bgm').paused,"
                        "t:document.getElementById('bgm').currentTime,"
                        "dur:document.getElementById('bgm').duration})")
        print("BGM после Старт:", a)

        # до сцены «Екатерина Ивановна» (реплика Сергея)
        g = 0
        while g < 40:
            s = state()
            if s["c"] == "Екатерина Ивановна" and "Лихнецкий" in s["n"]:
                break
            advance(); g += 1
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(SHOTS, "02_kate_dialog.png"))
        print("frame2:", state())

        # до аллеи (реплика поэта)
        g = 0
        while g < 120:
            s = state()
            if s["c"] == "На аллее" and "Лёша" in s["n"]:
                break
            advance(); g += 1
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(SHOTS, "03_alley.png"))
        print("frame3:", state())

        # до финала
        g = 0
        while g < 160:
            if pg.evaluate("document.getElementById('end').classList.contains('show')"):
                break
            advance(); g += 1
        pg.wait_for_timeout(1600)   # ждём автоплей тизера на финале
        ended = pg.evaluate("document.getElementById('end').classList.contains('show')")
        print("end shown:", ended, "| cinema open:", pg.evaluate("!document.getElementById('cinema').hidden"))
        pg.screenshot(path=os.path.join(SHOTS, "04_end.png"))

        br.close()
    httpd.shutdown()
    print("shots ->", SHOTS)


if __name__ == "__main__":
    main()
