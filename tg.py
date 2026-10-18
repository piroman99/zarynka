# -*- coding: utf-8 -*-
"""Минимальный клиент Telegram Bot API (stdlib) для канала «Зарянка».

Токен: `.tg_token` (chmod 600, git-ignored) или env TG_TOKEN.
Канал: https://t.me/zaryanka_vn (бот должен быть админом канала с правом «Публикация сообщений»).

⚠️ Сеть: из песочницы агента Telegram недоступен (api.telegram.org → Errno 101,
нужен хост в outbound-allowlist). Скрипт рассчитан на запуск там, где сеть открыта.

Команды:
  whoami                     — кто мы (getMe) и что видит бот в канале
  info                       — описание/имя/число подписчиков канала (getChat)
  desc "<текст>"             — поставить описание канала (бот-админ)
  title "<название>"         — переименовать канал
  post "<текст|@file>" [--video f] [--photo f] [--silent]
  edit <message_id> "<текст|@file>"
  pin <message_id>
"""
import os, sys, json, mimetypes, uuid
import urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.telegram.org/bot"
CHANNEL = os.environ.get("TG_CHANNEL", "@zaryanka_vn")


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
    url = API + token() + "/" + method
    data = json.dumps(params).encode() if params else None
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.loads(r.read().decode("utf-8"))
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
    req = urllib.request.Request(API + token() + "/" + method, data=body,
                                 headers={"Content-Type": ctype})
    with urllib.request.urlopen(req, timeout=600) as r:
        j = json.loads(r.read().decode("utf-8"))
    if not j.get("ok"):
        raise RuntimeError("%s: %s" % (method, j.get("description")))
    return j["result"]


def _text(arg):
    if arg.startswith("@"):
        with open(arg[1:], encoding="utf-8") as f:
            return f.read()
    return arg


def post(text, video=None, photo=None, silent=False):
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
        video = photo = None
        silent = "--silent" in argv
        rest = [a for a in argv[1:] if a != "--silent"]
        if "--video" in rest:
            i = rest.index("--video"); video = rest[i + 1]; rest = rest[:i] + rest[i + 2:]
        if "--photo" in rest:
            i = rest.index("--photo"); photo = rest[i + 1]; rest = rest[:i] + rest[i + 2:]
        res = post(_text(rest[0]), video=video, photo=photo, silent=silent)
        print("message_id:", res.get("message_id"))
    elif cmd == "edit":
        mid = int(argv[1])
        print(call("editMessageText", chat_id=CHANNEL, message_id=mid,
                   text=_text(argv[2]), parse_mode="HTML"))
    elif cmd == "pin":
        print(call("pinChatMessage", chat_id=CHANNEL, message_id=int(argv[1]),
                   disable_notification=True))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
