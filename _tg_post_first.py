# -*- coding: utf-8 -*-
"""Первый пост в канале «Зарянка» (t.me/zaryanka_vn) + тизер.

Текст — телеграм-версия поста E (ВК post_id 7), с двумя правками:
  * убран возраст Екатерины («Ей 68») — в рассказе возраста нет, цифра была моей выдумкой;
  * страниц приёмной 51 -> 57 (после разбивки абзацев на реплики).

Лимит подписи к видео в Telegram — 1024 символа, поэтому текст ужат под него.

Запуск:  python3 _tg_post_first.py --dry     # посчитать и показать
         python3 _tg_post_first.py --text    # только текст (лимит 4096)
         python3 _tg_post_first.py           # текст + видео out/avm_v3_epic.mp4
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tg

TEXT = """<b>Зарянка</b> — визуальная новелла по рассказу Александра «Котобус» Горбова.

В приёмную комиссию марсианской экспедиции входит женщина. Седые кудри, синий комбинезон на лямках, собственная исследовательская программа и очень спокойный взгляд на слово «невозможно». Инженер Лихнецкий собирается вежливо отказать. А потом будет Марс. Или Луна.

Первый эпизод собран — не макет и не раскадровка:

• Пролог. Семь кадров «кинохроники 2061»: Звёздный городок ранней весной, очередь у приёмной, значок с гравировкой. Текст — проза автора дословно.
• Приёмная. 57 страниц диалога. У Лихнецкого, Екатерины и Старика есть голоса и мимика — не одна картинка на всю сцену.
• Мелочи: подстрочник отдельно от голоса, музыка выключается совсем, на телефоне новелла разворачивается в портрет.

Превью открывается в браузере, ставить ничего не нужно:
https://piroman99.github.io/zarynka/

Здесь будем показывать кадры, голоса и то, как это делается.
ВКонтакте — https://vk.ru/zaryanka_vn

#Зарянка #визуальнаяновелла #космос"""

CAPTION_LIMIT = 1024


def main():
    print("chars:", len(TEXT), "| caption limit:", CAPTION_LIMIT, flush=True)
    if "--dry" in sys.argv:
        print("----")
        print(TEXT)
        print("----")
        return 0
    if "--text" in sys.argv:
        send = lambda: tg.post(TEXT)
    else:
        video = os.path.join(HERE, "out", "avm_v3_epic.mp4")
        print("video:", os.path.basename(video), os.path.getsize(video) // 1024, "KB", flush=True)
        send = lambda: tg.post(TEXT, video=video)

    res = None
    for attempt in range(5):
        try:
            res = send()
            break
        except RuntimeError as e:
            if "нет связи" in str(e) and attempt < 4:
                print("retry %d: %s" % (attempt + 1, str(e)[:120]), flush=True)
                time.sleep(3 + attempt * 2)
                continue
            raise
    print("message_id:", res.get("message_id"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
