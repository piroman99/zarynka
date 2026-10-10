# -*- coding: utf-8 -*-
"""Минимальный клиент VK API (stdlib) для оформления и публикаций сообщества «Зарянка».

Токены:
  • сообщества  — `.vk_token`   (env VK_TOKEN)      — обложка, посты, сообщения
  • пользователя — `.vk_user_token` (env VK_USER_TOKEN) — аватар, фото/видео в постах
Оба в .gitignore.

ВАЖНО про групповой токен (проверено 2026-10-10):
  разрешено: photos.getOwnerCoverPhotoUploadServer + saveOwnerCoverPhoto, wall.post, wall.edit,
             messages, docs(просмотр)
  запрещено (error 27 «unavailable with group auth»): photos.getWallUploadServer,
             photos.getUploadServer, photos.getOwnerPhotoUploadServer, video.save
  → аватар, фото и видео в постах требуют ПОЛЬЗОВАТЕЛЬСКОГО токена.

Команды:
  whoami                      — кто мы (группа)
  cover <file.png>            — поставить обложку сообщества
  avatar <file.png>           — поставить главную фотографию (нужен user-токен)
  post "<text|@file>" [--photo f]* [--video f]
"""
import os, sys, json, mimetypes, uuid, time
import urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.vk.com/method/"
V = "5.199"

def _read(env, fname):
    t = os.environ.get(env)
    if t:
        return t.strip()
    p = os.path.join(HERE, fname)
    if os.path.exists(p):
        with open(p) as f:
            return f.read().strip()
    return None

def token(kind="group"):
    t = _read("VK_TOKEN", ".vk_token") if kind == "group" else _read("VK_USER_TOKEN", ".vk_user_token")
    if not t:
        raise RuntimeError(f"нет токена ({kind}); нужен файл "
                           f"{'.vk_token' if kind=='group' else '.vk_user_token'}")
    return t

def call(method, kind="group", **params):
    params = {k: v for k, v in params.items() if v is not None}
    params["access_token"] = token(kind)
    params["v"] = V
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(API + method, data=data)
    with urllib.request.urlopen(req, timeout=60) as r:
        j = json.loads(r.read().decode("utf-8"))
    if "error" in j:
        raise RuntimeError(f"{method}: {j['error'].get('error_code')} {j['error'].get('error_msg')}")
    return j.get("response", j)

def _multipart(fields, file_field, file_path):
    boundary = "----nanobot" + uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    fn = os.path.basename(file_path)
    ct = mimetypes.guess_type(fn)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        content = f.read()
    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"{fn}\"\r\n"
             f"Content-Type: {ct}\r\n\r\n").encode()
    body += content + b"\r\n" + f"--{boundary}--\r\n".encode()
    return boundary, body

def upload(upload_url, file_field, file_path, tries=5):
    boundary, body = _multipart({}, file_field, file_path)
    last_err = None
    for a in range(tries):
        try:
            req = urllib.request.Request(
                upload_url, data=body,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:      # pu.vk.com иногда отдаёт 504 — повторяем
            last_err = e
            time.sleep(3)
    raise last_err

# ------------------------------------------------------------------ операции
def whoami():
    g = call("groups.getById")
    if isinstance(g, dict):
        g = g.get("groups", g)
    if isinstance(g, list):
        g = g[0]
    return g

def set_cover(path):
    gid = whoami()["id"]
    up = call("photos.getOwnerCoverPhotoUploadServer", group_id=gid,
              crop_x=0, crop_y=0, crop_x2=1590, crop_y2=400)["upload_url"]
    res = upload(up, "photo", path)
    return call("photos.saveOwnerCoverPhoto", hash=res["hash"], photo=res["photo"])

def set_avatar(path):
    gid = whoami()["id"]
    up = call("photos.getOwnerPhotoUploadServer", kind="user", owner_id=-gid)["upload_url"]
    res = upload(up, "photo", path)
    return call("photos.saveOwnerPhoto", kind="user", server=res["server"],
               hash=res["hash"], photo=res["photo"])

def upload_wall_photo(path):
    gid = whoami()["id"]
    up = call("photos.getWallUploadServer", kind="user", group_id=gid)["upload_url"]
    res = upload(up, "photo", path)
    p = call("photos.saveWallPhoto", kind="user", group_id=gid, server=res["server"],
             hash=res["hash"], photo=res["photo"])[0]
    return "photo%d_%d" % (p["owner_id"], p["id"])

def upload_video(path, name, description=""):
    gid = whoami()["id"]
    r = call("video.save", kind="user", group_id=gid, name=name,
             description=description, is_private=0)
    upload(r["upload_url"], "video_file", path)
    return "video%d_%d" % (r["owner_id"], r["video_id"])

def post(text, attachments=None):
    gid = whoami()["id"]
    return call("wall.post", owner_id=-gid, from_group=1, message=text,
                attachments=",".join(attachments) if attachments else None)

def edit(post_id, text, attachments=None):
    gid = whoami()["id"]
    return call("wall.edit", owner_id=-gid, post_id=post_id, message=text,
                attachments=",".join(attachments) if attachments else None)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "whoami"
    if cmd == "whoami":
        print(json.dumps(whoami(), ensure_ascii=False, indent=2))
    elif cmd == "cover":
        print(json.dumps(set_cover(sys.argv[2]), ensure_ascii=False)[:300])
    elif cmd == "avatar":
        print(json.dumps(set_avatar(sys.argv[2]), ensure_ascii=False)[:300])
    else:
        print("unknown:", cmd)
