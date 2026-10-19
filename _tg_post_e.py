# -*- coding: utf-8 -*-
"""Первый пост в Telegram-канале «Зарянка» (t.me/zaryanka_vn).

Текст — телеграм-версия поста E (ВК post_id 7), плюс тизер видео.
Запуск:  python3 _tg_post_e.py            (с тизером)
         python3 _tg_post_e.py --text     (только текст)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tg

TEXT = """<b>Зарянка</b> — визуальная новелла по рассказу Александра «Котобус» Горбова.

В приёмную комиссию марсианской экспедиции входит женщина. Ей 68. Седые кудри, синий комбинезон на лямках, собственная исследовательская программа и очень спокойный взгляд на слово «невозможно». Инженер Лихнецкий собирается вежливо отказать. А потом будет Марс. Или Луна.

Первый эпизод собран — не макет и не раскадровка:

• Пролог. Семь кадров «кинохроники 2061»: Звёздный городок ранней весной, очередь у приёмной, значок с гравировкой. Текст — проза автора дословно.
• Приёмная. 51 страница диалога. У Лихнецкого, Екатерины и Старика есть голоса и мимика — не одна картинка на всю сцену.
• Мелочи: подстрочник отдельно от голоса, музыка выключается совсем, на телефоне новелла разворачивается в портрет.

Превью открывается в браузере, ставить ничего не нужно:
https://piroman99.github.io/zaryanka/

Здесь будем показывать кадры, голоса и то, как это делается.
ВКонтакте — https://vk.ru/zaryanka_vn

#Зарянка #визуальнаяновелла #космос"""

if __name__ == "__main__":
    import time
    print("chars:", len(TEXT))
    if "--text" in sys.argv:
        send = lambda: tg.post(TEXT)
    else:
        video = os.path.join(HERE, "out", "avm_v3_epic.mp4")
        print("video:", os.path.basename(video), os.path.getsize(video) // 1024, "KB")
        send = lambda: tg.post(TEXT, video=video)

    # Сеть до Telegram флапает (РКН/DPI): одна неудача внутри tg.py не решает —
    # повторяем весь запрос, пока не пройдёт.
    res = None
    for attempt in range(5):
        try:
            res = send()
            break
        except RuntimeError as e:
            msg = str(e)
            if "нет связи" in msg and attempt < 4:
                print("retry %d: %s" % (attempt + 1, msg[:120]))
                time.sleep(3 + attempt * 2)
                continue
            raise
    print("message_id:", res.get("message_id"))
