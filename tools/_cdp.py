# -*- coding: utf-8 -*-
"""Мини-CDP: headless Chromium + ручной WebSocket (никаких зависимостей).
Умеет: navigate, evaluate, screenshot, ждать условие. Нужен для честной проверки движка.
"""
import os, io, json, base64, socket, struct, subprocess, time, glob, tempfile, urllib.request, shutil

WS_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CHROME = glob.glob(os.path.join(WS_ROOT, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]


class _WS:
    def __init__(self, url):
        assert url.startswith('ws://'), url
        rest = url[5:]
        hostport, _, path = rest.partition('/')
        path = '/' + path
        host, _, port = hostport.partition(':')
        self.s = socket.create_connection((host, int(port)), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        req = ('GET %s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
               'Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n' % (path, hostport, key))
        self.s.sendall(req.encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise ConnectionError('no handshake')
            buf += chunk
        head, _, self.buf = buf.partition(b'\r\n\r\n')
        if b'101' not in head.split(b'\r\n')[0]:
            raise ConnectionError('bad handshake: %r' % head[:120])

    def send(self, obj):
        data = json.dumps(obj).encode()
        mask = os.urandom(4)
        n = len(data)
        if n < 126:
            hdr = struct.pack('!BB', 0x81, 0x80 | n)
        elif n < 65536:
            hdr = struct.pack('!BBH', 0x81, 0x80 | 126, n)
        else:
            hdr = struct.pack('!BBQ', 0x81, 0x80 | 127, n)
        self.s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(1 << 20)
            if not chunk:
                raise ConnectionError('closed')
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        while True:
            b1, b2 = self._read(2)
            op, ln = b1 & 0x0f, b2 & 0x7f
            if ln == 126:
                ln = struct.unpack('!H', self._read(2))[0]
            elif ln == 127:
                ln = struct.unpack('!Q', self._read(8))[0]
            payload = self._read(ln) if ln else b''
            if op == 0x1:
                return json.loads(payload.decode())
            if op == 0x8:
                raise ConnectionError('close frame')
            if op == 0x9:
                mask = os.urandom(4)
                hdr = struct.pack('!BB', 0x8A, 0x80 | len(payload))
                self.s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))
            continue

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


class Browser:
    def __init__(self, width=1600, height=900):
        self.profile = tempfile.mkdtemp(prefix='cdp-')
        self.p = subprocess.Popen(
            [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
             '--autoplay-policy=no-user-gesture-required',
             '--window-size=%d,%d' % (width, height),
             '--user-data-dir=' + self.profile,
             '--remote-debugging-port=0', 'about:blank'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ws_url, deadline = None, time.time() + 40
        while time.time() < deadline:
            line = self.p.stderr.readline()
            if 'DevTools listening on' in line:
                ws_url = line.split('DevTools listening on', 1)[1].strip()
                break
        if not ws_url:
            raise RuntimeError('DevTools не поднялся')
        port = ws_url.rsplit(':', 1)[1].split('/')[0]
        for _ in range(60):
            try:
                data = json.load(urllib.request.urlopen('http://127.0.0.1:%s/json/list' % port, timeout=5))
                pages = [t for t in data if t.get('type') == 'page']
                if pages:
                    self.ws = _WS(pages[0]['webSocketDebuggerUrl'])
                    break
            except Exception:
                pass
            time.sleep(0.3)
        else:
            raise RuntimeError('нет page-таргета')
        self._id = 0
        self.logs = []
        self.send('Runtime.enable')
        self.send('Log.enable')
        self.send('Page.enable')

    def send(self, method, **params):
        self._id += 1
        mid = self._id
        self.ws.send({'id': mid, 'method': method, 'params': params})
        while True:
            msg = self.ws.recv()
            if msg.get('id') == mid:
                if 'error' in msg:
                    raise RuntimeError(method + ': ' + json.dumps(msg['error'])[:300])
                return msg.get('result', {})
            ev = msg.get('method')
            if ev in ('Runtime.consoleAPICalled', 'Runtime.exceptionThrown', 'Log.entryAdded'):
                self.logs.append(msg)

    def navigate(self, url, wait=0):
        self.send('Page.navigate', url=url)
        if wait:
            time.sleep(wait)

    def js(self, expr):
        r = self.send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True)
        return r.get('result', {}).get('value')

    def shot(self, path, full=False):
        params = {'format': 'png'}
        r = self.send('Page.captureScreenshot', **params)
        open(path, 'wb').write(base64.b64decode(r['data']))
        return path

    def wait_js(self, expr, timeout=60, every=0.25):
        end = time.time() + timeout
        while time.time() < end:
            try:
                if self.js(expr):
                    return True
            except Exception:
                pass
            time.sleep(every)
        return False

    def errors(self):
        out = []
        for m in self.logs:
            if m.get('method') == 'Runtime.exceptionThrown':
                d = m['params']['exceptionDetails']
                out.append('EXC: ' + (d.get('text', '') + ' ' + str(d.get('exception', {}).get('description', '')))[:200])
            elif m.get('method') == 'Log.entryAdded':
                e = m['params']['entry']
                if e.get('level') == 'error':
                    out.append('LOG: ' + str(e.get('text'))[:200])
            elif m.get('method') == 'Runtime.consoleAPICalled' and m['params'].get('type') == 'error':
                out.append('CONSOLE: ' + str(m['params'].get('args'))[:200])
        return out

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
        try:
            self.p.terminate()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()
        shutil.rmtree(self.profile, ignore_errors=True)
