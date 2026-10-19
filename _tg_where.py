# -*- coding: utf-8 -*-
"""Быстрая проверка: где бот состоит и что может. Не висит на флапе сети."""
import sys, json
sys.path.insert(0, "/home/ivan/.nanobot/workspace/novella/zaryanka")
import tg

CANDIDATES = [
    ("channel @zaryanka_vn", tg.CHANNEL),
    ("linked group -1004313670543", -1004313670543),
]

me = tg.call("getMe")
print("bot:", me.get("username"), me.get("id"), flush=True)

for label, cid in CANDIDATES:
    try:
        chat = tg.call("getChat", chat_id=cid)
        print(f"\n[{label}] title={chat.get('title')} type={chat.get('type')} "
              f"username={chat.get('username')}", flush=True)
    except Exception as e:
        print(f"\n[{label}] getChat FAIL: {str(e)[:120]}", flush=True)
        continue
    try:
        m = tg.call("getChatMember", chat_id=cid, user_id=me["id"])
        print(f"  member status={m.get('status')} "
              f"can_post={m.get('can_post_messages')} "
              f"can_send={m.get('can_send_messages')}", flush=True)
    except Exception as e:
        print(f"  getChatMember FAIL: {str(e)[:120]}", flush=True)
