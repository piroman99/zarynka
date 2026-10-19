# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, "/home/ivan/.nanobot/workspace/novella/zaryanka")
import tg

me = tg.call("getMe")
print("bot:", json.dumps(me, ensure_ascii=False))
print("link:", "https://t.me/" + me.get("username", "?"))

try:
    ch = tg.call("getChat", chat_id=tg.CHANNEL)
    print("chat:", json.dumps(ch, ensure_ascii=False)[:400])
except Exception as e:
    print("getChat FAIL:", e)

for meth in ("getChatAdministrators", "getChatMemberCount"):
    try:
        print(meth, json.dumps(tg.call(meth, chat_id=tg.CHANNEL), ensure_ascii=False)[:600])
    except Exception as e:
        print(meth, "FAIL:", e)
