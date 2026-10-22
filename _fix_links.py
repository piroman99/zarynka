# -*- coding: utf-8 -*-
"""Починить опечатку в демо-ссылке уже опубликованных постов.

Было: https://piroman99.github.io/zaryanka/  (404)
Стало: https://piroman99.github.io/zarynka/  (200, проверено)

Правит: TG #6 (видео, caption), TG #7 (аудио, caption), ВК #8 (текст стены).
Запуск: python3 _fix_links.py --dry | tg | vk | all
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tg
import vk

BAD = "https://piroman99.github.io/zaryanka/"
GOOD = "https://piroman99.github.io/zarynka/"

# TG #6 — подпись к тизеру, полный текст (без ссылки на ВК там её нет)
TG6 = """<b>Зарянка</b> — визуальная новелла по рассказу Александра «Котобус» Горбова.

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

# TG #7 — подпись к аудио-тизеру, с возвращённой (правильной) ссылкой
TG7 = """🎙 Как звучит приёмная

Первая сцена «Зарянки» озвучена целиком — 57 страниц диалога, три голоса.

Сергей Лихнецкий — Gemini «Charon». Старик — Gemini «Fenrir». Екатерина Ивановна — ElevenLabs «Charlotte»: перебрали девять кандидатов, и только она звучала так, что хочется верить.

В записи — шесть реплик из приёмной: знакомство, вопрос про возраст и отказ. Закадровый голос пока не показываем, его ещё выбираем.

Послушать новеллу в браузере, ничего не устанавливая:
https://piroman99.github.io/zarynka/

ВКонтакте — https://vk.ru/zaryanka_vn

#Зарянка #визуальнаяновелла #озвучка"""

# ВК #8 — текст поста на стене
VK8 = """🎙 Как звучит приёмная

Первая сцена «Зарянки» озвучена целиком — 57 страниц диалога, три голоса.

Сергей Лихнецкий — Gemini «Charon». Старик — Gemini «Fenrir». Екатерина Ивановна — ElevenLabs «Charlotte»: перебрали девять кандидатов, и только она звучала так, что хочется верить.

Открывается в браузере, ставить ничего не нужно — включите звук:
https://piroman99.github.io/zarynka/

Шесть реплик из приёмной — знакомство, вопрос про возраст и отказ — выложили в Telegram-канале: https://t.me/zaryanka_vn

#Зарянка #визуальнаяновелла #озвучка"""

TG_POSTS = {6: TG6, 7: TG7}


def fix_tg():
    for mid, text in TG_POSTS.items():
        assert BAD not in text, mid
        print("TG #%d: %d знаков" % (mid, len(text)), flush=True)
        for attempt in range(4):
            try:
                tg.call("editMessageCaption", chat_id=tg.CHANNEL, message_id=mid,
                        caption=text, parse_mode="HTML")
                print("  ok", flush=True)
                break
            except RuntimeError as e:
                if "нет связи" in str(e) and attempt < 3:
                    print("  retry:", str(e)[:100], flush=True)
                    time.sleep(3)
                    continue
                raise


def fix_vk():
    assert BAD not in VK8
    print("VK #8: %d знаков" % len(VK8), flush=True)
    print("  ", vk.edit(8, VK8), flush=True)


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    want = [a for a in sys.argv[1:] if a in ("tg", "vk")] or ["tg", "vk"]
    if dry:
        for mid, t in TG_POSTS.items():
            print("TG #%d: %d знаков, ссылка %s" % (mid, len(t), GOOD in t))
        print("VK #8: %d знаков, ссылка %s" % (len(VK8), GOOD in VK8))
        raise SystemExit(0)
    if "tg" in want:
        fix_tg()
    if "vk" in want:
        fix_vk()
