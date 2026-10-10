# -*- coding: utf-8 -*-
"""Проверка подключения PlusVibe. Запуск: python3 pv_test.py [--gen]
Без ключа покажет, что ключ не найден (это ожидаемо до шага 2).
"""
import sys, json
import pv

try:
    key = pv._read_key()
    print("ключ найден:", key[:7] + "…" if len(key) > 7 else "(короткий!)")
except Exception as e:
    print("КЛЮЧ:", e)
    print("\nДальше: создайте .pv_key или .api_keys.json рядом с этим файлом.")
    sys.exit(0)

print("\n--- баланс ---")
print(json.dumps(pv.balance(), ensure_ascii=False, indent=2))

model = "gpt-image-2"   # 0.45 ₽/изобр. (text+image), дёшево и умеет референс
prompt = ("пожилая женщина с седыми кудрями и голубыми глазами в синем рабочем "
          "комбинезоне на лямках, стоит у двери с табличкой «ПРИЁМНАЯ КОМИССИЯ», "
          "тёплый дневной свет, реалистичная живопись, кинематографично")

print(f"\n--- оценка цены для {model} ---")
try:
    print(json.dumps(pv.price(model, prompt, {"aspect_ratio": "16:9"}), ensure_ascii=False, indent=2))
except Exception as e:
    print("price:", e)

if "--gen" in sys.argv:
    print(f"\n--- генерация тестового кадра ({model}) ---")
    files, st = pv.generate_to_files(model, prompt, {"aspect_ratio": "16:9"},
                                     outdir="assets/gen", name="test", max_price_rub=10)
    print("файлы:", files)
