# -*- coding: utf-8 -*-
"""Новый пост в «Зарянку» — про голоса приёмной.

Telegram: аудио-фрагмент (out/reception_voices.mp3, 26 с) + подпись.
ВКонтакте: только текст (групповой токен не даёт ни фото, ни видео, ни аудио)
           + ссылка на фрагмент в TG.

⚠️ Ссылки на демо (piroman99.github.io/zaryanka) в постах НЕТ: 2026-10-22
проверено — Pages на репозитории выключен, отдаёт 404 (api /pages → 404).
Когда Иван включит Pages, ссылку можно вернуть правкой: `tg.py edit <id>`
и `vk.py` → wall.edit.

Запуск:  python3 _post_voices.py --dry          # показать тексты и длины
         python3 _post_voices.py tg             # только Telegram
         python3 _post_voices.py vk             # только ВК
         python3 _post_voices.py                # обе площадки
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tg
import vk

AUDIO = os.path.join(HERE, "out", "reception_voices.mp3")
CAPTION_LIMIT = 1024

TG_TEXT = """🎙 Как звучит приёмная

Первая сцена «Зарянки» озвучена целиком — 57 страниц диалога, три голоса.

Сергей Лихнецкий — Gemini «Charon». Старик — Gemini «Fenrir». Екатерина Ивановна — ElevenLabs «Charlotte»: перебрали девять кандидатов, и только она звучала так, что хочется верить.

В записи — шесть реплик из приёмной: знакомство, вопрос про возраст и отказ. Закадровый голос пока не показываем, его ещё выбираем.

ВКонтакте — https://vk.ru/zaryanka_vn

#Зарянка #визуальнаяновелла #озвучка"""

VK_TEXT = """🎙 Как звучит приёмная

Первая сцена «Зарянки» озвучена целиком — 57 страниц диалога, три голоса.

Сергей Лихнецкий — Gemini «Charon». Старик — Gemini «Fenrir». Екатерина Ивановна — ElevenLabs «Charlotte»: перебрали девять кандидатов, и только она звучала так, что хочется верить.

Шесть реплик из приёмной — знакомство, вопрос про возраст и отказ — выложили в Telegram-канале: https://t.me/zaryanka_vn

#Зарянка #визуальнаяновелла #озвучка"""


def main():
    dry = "--dry" in sys.argv
    want = [a for a in sys.argv[1:] if a in ("tg", "vk")] or ["tg", "vk"]

    print("TG caption:", len(TG_TEXT), "/", CAPTION_LIMIT)
    print("VK text   :", len(VK_TEXT))
    if len(TG_TEXT) > CAPTION_LIMIT:
        print("!! подпись TG длиннее лимита")
        return 1
    print("audio     :", os.path.basename(AUDIO),
          os.path.getsize(AUDIO) // 1024, "KB")

    if dry:
        for name, txt in (("TG", TG_TEXT), ("VK", VK_TEXT)):
            print("\n===== %s =====\n%s" % (name, txt))
        return 0

    if "tg" in want:
        res = None
        for attempt in range(5):
            try:
                res = tg.post(TG_TEXT, audio=AUDIO, title="Приёмная — голоса",
                              performer="Зарянка")
                break
            except RuntimeError as e:
                if "нет связи" in str(e) and attempt < 4:
                    print("tg retry %d: %s" % (attempt + 1, str(e)[:120]), flush=True)
                    time.sleep(3 + attempt * 2)
                    continue
                raise
        print("TG message_id:", res.get("message_id"), flush=True)

    if "vk" in want:
        res = vk.post(VK_TEXT)
        print("VK wall.post:", res, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
