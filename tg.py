# -*- coding: utf-8 -*-
"""Минимальный клиент Telegram Bot API (stdlib) для канала «Зарянка».

Токен: `.tg_token` (chmod 600, git-ignored) или env TG_TOKEN.
Канал: https://t.me/zaryanka_vn (бот должен быть админом канала с правом «Публикация сообщений»).

⚠️ Сеть: это блокировка РКН/DPI на стороне провайдера, НЕ песочница агента и НЕ
allowlist (никакого egress-allowlist в nanobot нет, DNS резолвится, локального прокси нет).
Симптом: TCP до DC Telegram флапает (таймаут, со следующей попытки TLS 1.3 OK) —
поэтому ходим на IP с server_hostname=api.telegram.org и ретраим. Проверено 2026-10-19.

Команды:
  whoami                     — кто мы (getMe) и что видит бот в канале
  info                       — описание/имя/число подписчиков канала (getChat)
  desc "<текст>"             — поставить описание канала (бот-админ)
  title "<название>"         — переименовать канал
  post "<текст|@file>" [--video f] [--photo f] [--audio f] [--silent]
  edit <message_id> "<текст|@file>"
  pin <message_id>
  del <message_id>           — удалить сообщение канала
"""
import os, sys, json, mimetypes, uuid, socket, ssl, time
import urllib.request, urllib.error, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
API_HOST = "api.telegram.org"
# Прямой DNS для api.telegram.org из этой сети режется (Errno 101 / timeout), но сами DC
# Telegram открыты и отдают Bot API при правильном SNI. Соединение при этом флапает
# (примерно 1 из 2 попыток) → ходим на IP с server_hostname=api.telegram.org и ретраим.
# Проверено 2026-10-18. Переопределяется TG_API_IPS (список через запятую).
API_IPS = [ip.strip() for ip in os.environ.get(
    "TG_API_IPS", "149.154.167.220,149.154.167.197,149.154.175.50").split(",") if ip.strip()]
CHANNEL = os.environ.get("TG_CHANNEL", "@zaryanka_vn")


def _pinned(method_name, body, ctype, timeout=300, attempts=8):
    """Запрос на IP с SNI/Host = api.telegram.org (обход блокировки по DNS), с ретраями."""
    path = "/bot" + token() + "/" + method_name
    last = None
    for i in range(attempts):
        ip = API_IPS[i % len(API_IPS)]
        ctx = ssl.create_default_context()
        try:
            s = socket.create_connection((ip, 443), timeout=12)
            ss = ctx.wrap_socket(s, server_hostname=API_HOST)
        except Exception as e:
            last = e
            time.sleep(1.5 + i)
            continue
        head = ["%s %s HTTP/1.1" % ("POST" if body is not None else "GET", path),
                "Host: " + API_HOST,
                "Connection: close"]
        if body is not None:
            head.append("Content-Type: " + ctype)
            head.append("Content-Length: %d" % len(body))
        try:
            ss.sendall(("\r\n".join(head) + "\r\n\r\n").encode() + (body or b""))
            ss.settimeout(timeout)
            raw = b""
            while True:
                try:
                    chunk = ss.recv(65536)
                except socket.timeout:
                    break
                if not chunk:
                    break
                raw += chunk
        except Exception as e:
            last = e
            ss.close()
            time.sleep(1.5 + i)
            continue
        ss.close()
        head_b, _, payload = raw.partition(b"\r\n\r\n")
        status = head_b.split(b"\r\n")[0].decode("latin-1")
        if not payload:
            last = RuntimeError("пустой ответ (%s)" % status)
            time.sleep(1.5 + i)
            continue
        if b"chunked" in head_b.lower():
            out, rest = b"", payload
            while True:
                line, _, rest = rest.partition(b"\r\n")
                try:
                    n = int(line.strip().split(b";")[0], 16)
                except ValueError:
                    break
                if n == 0:
                    break
                out += rest[:n]
                rest = rest[n + 2:]
            payload = out
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            last = RuntimeError("не JSON (%s): %r" % (status, payload[:120]))
            time.sleep(1.5 + i)
    raise RuntimeError("%s: нет связи с Telegram после %d попыток (%s)"
                       % (method_name, attempts, last))


def _http(method_name, body=None, ctype="application/json", timeout=300):
    """Сначала обычный https, при сетевой ошибке — запиненный IP."""
    path = "/bot" + token() + "/" + method_name
    url = "https://" + API_HOST + path
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": ctype} if body is not None else {})
    try:
        with urllib.request.urlopen(req, timeout=min(timeout, 10)) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8"))
        except Exception:
            raise RuntimeError("%s: HTTP %s" % (method_name, e.code))
    except (urllib.error.URLError, socket.timeout, OSError):
        return _pinned(method_name, body, ctype, timeout=timeout)


def token():
    t = os.environ.get("TG_TOKEN")
    if t:
        return t.strip()
    p = os.path.join(HERE, ".tg_token")
    if os.path.exists(p):
        with open(p) as f:
            return f.read().strip()
    raise RuntimeError("нет токена: положи его в novella/zaryanka/.tg_token "
                       "(chmod 600) или задай env TG_TOKEN")


def call(method, **params):
    params = {k: v for k, v in params.items() if v is not None}
    body = json.dumps(params).encode() if params else b"{}"
    j = _http(method, body, "application/json")
    if not j.get("ok"):
        raise RuntimeError("%s: %s" % (method, j.get("description")))
    return j["result"]


def _multipart(fields, file_field, file_path):
    boundary = "----nanobot" + uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        if v is None:
            continue
        body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                 % (boundary, k, v)).encode()
    ctype = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    fname = os.path.basename(file_path)
    body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
             "Content-Type: %s\r\n\r\n" % (boundary, file_field, fname, ctype)).encode()
    with open(file_path, "rb") as f:
        body += f.read()
    body += ("\r\n--%s--\r\n" % boundary).encode()
    return body, "multipart/form-data; boundary=" + boundary


def send_file(method, file_field, path, **fields):
    body, ctype = _multipart(fields, file_field, path)
    j = _http(method, body, ctype, timeout=600)
    if not j.get("ok"):
        raise RuntimeError("%s: %s" % (method, j.get("description")))
    return j["result"]


def _text(arg):
    if arg.startswith("@"):
        with open(arg[1:], encoding="utf-8") as f:
            return f.read()
    return arg


def post(text, video=None, photo=None, audio=None, title=None, performer=None,
         duration=None, silent=False):
    kw = dict(chat_id=CHANNEL, parse_mode="HTML",
              link_preview_options=json.dumps({"is_disabled": False}),
              disable_notification=True if silent else None)
    if video:
        kw["caption"] = text
        kw["supports_streaming"] = True
        return send_file("sendVideo", "video", video, **kw)
    if photo:
        kw["caption"] = text
        return send_file("sendPhoto", "photo", photo, **kw)
    if audio:
        kw["caption"] = text
        if title:
            kw["title"] = title
        if performer:
            kw["performer"] = performer
        if duration:
            kw["duration"] = int(duration)
        return send_file("sendAudio", "audio", audio, **kw)
    kw["text"] = text
    return call("sendMessage", **kw)


def whoami():
    me = call("getMe")
    out = {"bot": me.get("username"), "id": me.get("id")}
    try:
        ch = call("getChat", chat_id=CHANNEL)
        out["channel"] = {"id": ch.get("id"), "title": ch.get("title"),
                          "username": ch.get("username"),
                          "description": ch.get("description"),
                          "subscribers": ch.get("member_count")}
    except Exception as e:
        out["channel_error"] = str(e)
    return out


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd == "whoami":
        print(json.dumps(whoami(), ensure_ascii=False, indent=2))
    elif cmd == "info":
        ch = call("getChat", chat_id=CHANNEL)
        print(json.dumps({k: ch.get(k) for k in
                          ("id", "title", "username", "description", "member_count")},
                         ensure_ascii=False, indent=2))
    elif cmd == "desc":
        print(call("setChatDescription", chat_id=CHANNEL, description=_text(argv[1])))
    elif cmd == "title":
        print(call("setChatTitle", chat_id=CHANNEL, title=argv[1]))
    elif cmd == "post":
        video = photo = audio = None
        silent = "--silent" in argv
        rest = [a for a in argv[1:] if a != "--silent"]
        for flag in ("--video", "--photo", "--audio"):
            if flag in rest:
                i = rest.index(flag)
                val = rest[i + 1]
                rest = rest[:i] + rest[i + 2:]
                if flag == "--video":
                    video = val
                elif flag == "--photo":
                    photo = val
                else:
                    audio = val
        res = post(_text(rest[0]), video=video, photo=photo, audio=audio, silent=silent)
        print("message_id:", res.get("message_id"))
    elif cmd == "edit":
        mid = int(argv[1])
        txt = _text(argv[2])
        try:
            print(call("editMessageText", chat_id=CHANNEL, message_id=mid,
                       text=txt, parse_mode="HTML"))
        except RuntimeError:
            # у медиа-сообщений текст живёт в caption
            print(call("editMessageCaption", chat_id=CHANNEL, message_id=mid,
                       caption=txt, parse_mode="HTML"))
    elif cmd == "pin":
        print(call("pinChatMessage", chat_id=CHANNEL, message_id=int(argv[1]),
                   disable_notification=True))
    elif cmd in ("del", "delete"):
        # Бот-админ с правом «Удаление сообщений» может снести любой пост канала.
        ok = call("deleteMessage", chat_id=CHANNEL, message_id=int(argv[1]))
        print("deleted" if ok else ok)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
